import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        muted: "#687385",
        line: "#d9dee8",
        surface: "#f7f8fb",
        brand: "#d83a56",
        accent: "#276f86",
        green: "#24845d"
      }
    }
  },
  plugins: []
};

export default config;
