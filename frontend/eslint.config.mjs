import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const config = [...nextCoreWebVitals, ...nextTs, { ignores: [".next/**", "node_modules/**", "next-env.d.ts"] }];
export default config;
