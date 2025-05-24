import React from 'react';
import { Box } from '@mui/material';
import Editor from '@monaco-editor/react';

interface EditorProps {
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
}

export function HtmlEditor({ value, onChange, readOnly = false }: EditorProps) {
  return (
    <Box sx={{ mt: 2, height: '500px', border: '1px solid #ccc' }}>
      <Editor
        height="100%"
        defaultLanguage="html"
        value={value}
        onChange={(value) => onChange(value || '')}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          wordWrap: 'on',
          automaticLayout: true,
          readOnly,
          suggestOnTriggerCharacters: !readOnly,
          quickSuggestions: !readOnly,
          snippetSuggestions: readOnly ? 'none' : 'inline',
          suggest: {
            showWords: !readOnly,
            showSnippets: !readOnly,
            showClasses: !readOnly,
            showFunctions: !readOnly,
            showVariables: !readOnly,
            showProperties: !readOnly,
            showColors: !readOnly,
            showFiles: !readOnly,
            showReferences: !readOnly,
            showFolders: !readOnly,
            showTypeParameters: !readOnly,
            showEnums: !readOnly,
            showEnumMembers: !readOnly,
            showKeywords: !readOnly
          }
        }}
      />
    </Box>
  );
} 