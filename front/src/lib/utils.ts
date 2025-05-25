/**
 * 날짜를 한국 시간 형식으로 포맷팅합니다.
 * @param date ISO 문자열 또는 Date 객체
 * @returns 포맷팅된 날짜 문자열 (YYYY.MM.DD HH:mm)
 */
export const formatDate = (date: string | Date | null): string => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
}; 