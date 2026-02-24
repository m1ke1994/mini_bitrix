export function formatDuration(value) {
  const totalSeconds = Math.max(0, Math.floor(Number(value) || 0));
  if (totalSeconds < 60) {
    return `${totalSeconds} сек`;
  }
  if (totalSeconds < 3600) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes} мин ${seconds} сек`;
  }
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  return `${hours} ч ${minutes} мин`;
}
