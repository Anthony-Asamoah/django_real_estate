// Block oversized files before upload (the host answers them with a bare 413).
document.addEventListener('change', (e) => {
  const input = e.target;
  if (input.type !== 'file' || !window.MAX_UPLOAD_MB) return;
  const max = window.MAX_UPLOAD_MB * 1024 * 1024;
  const big = [...input.files].find((f) => f.size > max);
  if (!big) return;
  input.value = '';
  alert(
    `"${big.name}" is ${(big.size / 1048576).toFixed(1)} MB, which is too large.\n` +
    `Please choose a file under ${window.MAX_UPLOAD_MB} MB (compress or resize it first).`
  );
});
