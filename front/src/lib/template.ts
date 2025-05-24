import { Environment } from 'nunjucks';

// Nunjucks 환경 설정
const env = new Environment(undefined, {
  autoescape: true,
  trimBlocks: true,
  lstripBlocks: true
});

// 템플릿 렌더링 함수
export async function renderTemplate(template: string, data: any): Promise<string> {
  try {
    return env.renderString(template, data);
  } catch (error) {
    console.error('템플릿 렌더링 오류:', error);
    throw error;
  }
}

// 템플릿에서 사용된 변수 추출
export function extractVariables(template: string): string[] {
  const variables = new Set<string>();
  
  // {{ variable }} 패턴 찾기
  const expressionPattern = /{{([^}]+)}}/g;
  let match;
  while ((match = expressionPattern.exec(template)) !== null) {
    const expr = match[1].trim();
    // 필터 제거하고 변수만 추출
    const varName = expr.split('|')[0].trim();
    if (varName && !varName.startsWith('if') && !varName.startsWith('for')) {
      variables.add(varName);
    }
  }

  // {% if variable %} 패턴 찾기
  const blockPattern = /{%\s*(if|elif|for)\s+([^%]+)%}/g;
  while ((match = blockPattern.exec(template)) !== null) {
    const expr = match[2].trim();
    // 조건문에서 변수 추출
    const vars = expr.split(/\s+(and|or|in)\s+/);
    vars.forEach(v => {
      const varName = v.trim();
      if (varName && !varName.startsWith('if') && !varName.startsWith('for')) {
        variables.add(varName);
      }
    });
  }

  return Array.from(variables);
} 