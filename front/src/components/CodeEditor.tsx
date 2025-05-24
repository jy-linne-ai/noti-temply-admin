import React from 'react';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: string;
}

export function CodeEditor({ value, onChange, language = 'html', height = '300px' }: CodeEditorProps) {
  return (
    <Editor
      height={height}
      language={language}
      value={value}
      onChange={(value) => onChange(value || '')}
      options={{
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        wordWrap: 'on',
        automaticLayout: true,
      }}
    />
  );
} 