import {
  configureStore,
  createSlice,
  type PayloadAction,
} from "@reduxjs/toolkit";
import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { useDispatch, useSelector } from "react-redux";
import type { Input, Preset, Report } from "./types";

export const api = createApi({
  reducerPath: "compilerApi",
  baseQuery: fetchBaseQuery({ baseUrl: "/api" }),
  endpoints: (b) => ({
    presets: b.query<Preset[], void>({ query: () => "/presets" }),
    implementation: b.query<Record<string, string>, void>({
      query: () => "/implementation",
    }),
    analyze: b.mutation<Report, Input>({
      query: (body) => ({ url: "/analyze", method: "POST", body }),
    }),
  }),
});
interface Snapshot {
  input: Input;
  report: Report;
}
interface Workbench {
  input: Input;
  revision: number;
  preset: string;
  report: Report | null;
  reportRevision: number;
  pending: { id: string; revision: number } | null;
  error: string | null;
  baseline: Snapshot | null;
  pane: string;
  selectedFunction: string;
  selectedBlock: number;
}
const initialState: Workbench = {
  input: { Source: "", Filename: "editor.svc", Plan: "" },
  revision: 0,
  preset: "",
  report: null,
  reportRevision: -1,
  pending: null,
  error: null,
  baseline: null,
  pane: "cfg",
  selectedFunction: "",
  selectedBlock: 0,
};
const workbench = createSlice({
  name: "workbench",
  initialState,
  reducers: {
    presetLoaded(s, a: PayloadAction<Preset>) {
      s.input = {
        Source: a.payload.Source,
        Filename: a.payload.Filename,
        Plan: a.payload.Plan,
      };
      s.preset = a.payload.ID;
      s.revision++;
      s.selectedFunction = "";
      s.selectedBlock = 0;
      s.error = null;
    },
    edited(s, a: PayloadAction<{ field: "Source" | "Plan"; value: string }>) {
      s.input[a.payload.field] = a.payload.value;
      s.revision++;
    },
    started(s, a: PayloadAction<{ id: string; revision: number }>) {
      s.pending = a.payload;
      s.error = null;
    },
    finished(
      s,
      a: PayloadAction<{ id: string; revision: number; report: Report }>,
    ) {
      if (s.pending?.id !== a.payload.id) return;
      s.report = a.payload.report;
      s.reportRevision = a.payload.revision;
      s.pending = null;
    },
    failed(s, a: PayloadAction<{ id: string; message: string }>) {
      if (s.pending?.id !== a.payload.id) return;
      s.pending = null;
      s.error = a.payload.message;
    },
    pin(s) {
      if (s.report && s.reportRevision === s.revision)
        s.baseline = { input: { ...s.input }, report: s.report };
    },
    clearBaseline(s) {
      s.baseline = null;
    },
    pane(s, a: PayloadAction<string>) {
      s.pane = a.payload;
    },
    selectFunction(s, a: PayloadAction<string>) {
      s.selectedFunction = a.payload;
      s.selectedBlock = 0;
    },
    selectBlock(s, a: PayloadAction<number>) {
      s.selectedBlock = a.payload;
    },
  },
});
export const actions = workbench.actions;
export const store = configureStore({
  reducer: { workbench: workbench.reducer, [api.reducerPath]: api.reducer },
  middleware: (g) => g().concat(api.middleware),
});
export const useAppDispatch = useDispatch.withTypes<typeof store.dispatch>();
export const useAppSelector =
  useSelector.withTypes<ReturnType<typeof store.getState>>();
