"use client";

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export type Settings = {
  boardTheme: "walnut" | "parchment" | "steel";
  pieceSet: "cburnett" | "merida";
  sound: boolean;
  showDots: boolean;
  showCoords: boolean;
  autoPromoteQueen: boolean;
  displayName?: string;
};

type SettingsActions = {
  set: <K extends keyof Settings>(key: K, value: Settings[K]) => void;
};

export const useSettings = create<Settings & SettingsActions>()(
  persist(
    (set) => ({
      boardTheme: "walnut",
      pieceSet: "cburnett",
      sound: true,
      showDots: true,
      showCoords: true,
      autoPromoteQueen: false,
      set: (key, value) => set({ [key]: value } as Partial<Settings>),
    }),
    {
      name: "chess-room:settings",
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
