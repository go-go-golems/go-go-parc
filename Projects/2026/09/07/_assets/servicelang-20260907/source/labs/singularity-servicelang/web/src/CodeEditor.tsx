import { useEffect, useRef } from "react";
import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";
import { keymap } from "@codemirror/view";
import { StreamLanguage } from "@codemirror/language";
import { json } from "@codemirror/lang-json";
import { cpp } from "@codemirror/lang-cpp";
import { go } from "@codemirror/legacy-modes/mode/go";
import { oneDark } from "@codemirror/theme-one-dark";
import type { Span } from "./types";

const svc = StreamLanguage.define({
  token(s) {
    if (s.match("//")) {
      s.skipToEnd();
      return "comment";
    }
    if (s.match(/\b(use|fn|own|move|let|if|else|match|return|true|false)\b/))
      return "keyword";
    if (s.match(/\b[A-Z][A-Za-z0-9_]*\b/)) return "typeName";
    if (s.match(/-?\d+/)) return "number";
    s.next();
    return null;
  },
});
export function bytePosition(text: string, byte: number) {
  let consumed = 0,
    offset = 0;
  const encoder = new TextEncoder();
  for (const char of text) {
    const n = encoder.encode(char).length;
    if (consumed + n > byte) break;
    consumed += n;
    offset += char.length;
  }
  return offset;
}
interface Props {
  value: string;
  onChange?: (v: string) => void;
  language?: "svc" | "json" | "cpp" | "go";
  label: string;
  readOnly?: boolean;
  selection?: Span | null;
  onRun?: () => void;
}
export function CodeEditor({
  value,
  onChange,
  language = "svc",
  label,
  readOnly = false,
  selection,
  onRun,
}: Props) {
  const host = useRef<HTMLDivElement>(null),
    view = useRef<EditorView | null>(null),
    updating = useRef(false);
  const callbacks = useRef({ onChange, onRun });
  callbacks.current = { onChange, onRun };
  useEffect(() => {
    if (!host.current) return;
    const lang =
      language === "json"
        ? json()
        : language === "cpp"
          ? cpp()
          : language === "go"
            ? StreamLanguage.define(go)
            : svc;
    const v = new EditorView({
      parent: host.current,
      state: EditorState.create({
        doc: value,
        extensions: [
          basicSetup,
          lang,
          oneDark,
          EditorView.lineWrapping,
          EditorState.readOnly.of(readOnly),
          EditorView.editable.of(!readOnly),
          EditorView.contentAttributes.of({ "aria-label": label }),
          keymap.of([
            {
              key: "Mod-Enter",
              run: () => {
                callbacks.current.onRun?.();
                return true;
              },
            },
          ]),
          EditorView.updateListener.of((u) => {
            if (u.docChanged && !updating.current)
              callbacks.current.onChange?.(u.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = v;
    return () => {
      v.destroy();
      view.current = null;
    };
  }, [language, readOnly, label]);
  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== value) {
      updating.current = true;
      v.dispatch({
        changes: { from: 0, to: v.state.doc.length, insert: value },
      });
      updating.current = false;
    }
  }, [value]);
  useEffect(() => {
    const v = view.current;
    if (v && selection) {
      const text = v.state.doc.toString();
      v.dispatch({
        selection: {
          anchor: bytePosition(text, selection.Start),
          head: bytePosition(text, selection.End),
        },
        scrollIntoView: true,
      });
      v.focus();
    }
  }, [selection]);
  return <div className="code-editor" ref={host} />;
}
