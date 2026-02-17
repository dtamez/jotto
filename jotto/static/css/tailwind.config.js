module.exports = {
  content: ["./ltw/**/*.html"],
  safelist: ["bg-green-500", "bg-yellow-500"],
  theme: { extend: {} },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light"],
  },
};
