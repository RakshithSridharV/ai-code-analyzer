import React from 'react';
import Editor from 'react-simple-code-editor';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-java';
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';
import 'prismjs/themes/prism-twilight.css';

export default function CodeEditor({ code, setCode, language, setLanguage, onAnalyze, isAnalyzing }) {
  // Vite sometimes imports CommonJS default exports as an object { default: Component }
  const EditorComponent = Editor.default || Editor;

  const highlight = (code) => {
    let lang = language === 'auto' ? 'javascript' : language;
    // Map our backend language key to Prism's grammar name
    if (lang === 'cpp') lang = 'cpp';
    if (lang === 'c')   lang = 'c';
    try {
      return Prism.highlight(code, Prism.languages[lang] || Prism.languages.javascript, lang);
    } catch {
      return code;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="editor-header">
        <select 
          className="editor-select" 
          value={language} 
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="auto">Auto Detect</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
          <option value="c">C</option>
          <option value="cpp">C++</option>
        </select>
        <button 
          className="analyze-btn" 
          onClick={onAnalyze} 
          disabled={isAnalyzing || !code.trim()}
        >
          {isAnalyzing ? "Analyzing..." : "Analyze Code"}
        </button>
      </div>
      <div className="editor-body">
        <EditorComponent
          value={code}
          onValueChange={setCode}
          highlight={highlight}
          padding={15}
          style={{
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: 14,
            minHeight: '100%',
          }}
        />
      </div>
    </div>
  );
}
