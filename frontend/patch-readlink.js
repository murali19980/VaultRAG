const fs = require('fs');

const patchCallback = (target) => {
  if (!target) return;
  const originalReadlink = target.readlink;
  if (originalReadlink && !originalReadlink.__patched) {
    const patchedReadlink = function(path, options, callback) {
      const cb = typeof options === 'function' ? options : callback;
      const opts = typeof options === 'object' ? options : {};
      
      originalReadlink(path, opts, (err, linkString) => {
        if (err && err.code === 'EISDIR') {
          fs.lstat(path, (lstatErr, stats) => {
            if (!lstatErr && !stats.isSymbolicLink()) {
              const newErr = new Error(`EINVAL: invalid argument, readlink '${path}'`);
              newErr.code = 'EINVAL';
              newErr.errno = -4071;
              newErr.syscall = 'readlink';
              newErr.path = path;
              return cb(newErr);
            }
            cb(err);
          });
        } else {
          cb(err, linkString);
        }
      });
    };
    patchedReadlink.__patched = true;
    target.readlink = patchedReadlink;
  }

  const originalReadlinkSync = target.readlinkSync;
  if (originalReadlinkSync && !originalReadlinkSync.__patched) {
    const patchedReadlinkSync = function(path, options) {
      try {
        return originalReadlinkSync(path, options);
      } catch (err) {
        if (err.code === 'EISDIR') {
          const stats = fs.lstatSync(path);
          if (!stats.isSymbolicLink()) {
            const newErr = new Error(`EINVAL: invalid argument, readlink '${path}'`);
            newErr.code = 'EINVAL';
            newErr.errno = -4071;
            newErr.syscall = 'readlink';
            newErr.path = path;
            throw newErr;
          }
        }
        throw err;
      }
    };
    patchedReadlinkSync.__patched = true;
    target.readlinkSync = patchedReadlinkSync;
  }
};

const patchPromises = (target) => {
  if (!target) return;
  const originalReadlink = target.readlink;
  if (originalReadlink && !originalReadlink.__patched) {
    const patchedReadlink = async function(path, options) {
      try {
        return await originalReadlink(path, options);
      } catch (err) {
        if (err.code === 'EISDIR') {
          let stats;
          try {
            stats = await fs.promises.lstat(path);
          } catch (lstatErr) {
            // ignore lstat errors
          }
          if (stats && !stats.isSymbolicLink()) {
            const newErr = new Error(`EINVAL: invalid argument, readlink '${path}'`);
            newErr.code = 'EINVAL';
            newErr.errno = -4071;
            newErr.syscall = 'readlink';
            newErr.path = path;
            throw newErr;
          }
        }
        throw err;
      }
    };
    patchedReadlink.__patched = true;
    target.readlink = patchedReadlink;
  }
};

// Patch standard callback and sync API
patchCallback(fs);

// Patch fs.promises
if (fs.promises) {
  patchPromises(fs.promises);
}

// Patch fs/promises module if it is loaded
try {
  const fsPromises = require('fs/promises');
  patchPromises(fsPromises);
} catch (e) {}

console.log("Readlink patch loaded successfully.");
