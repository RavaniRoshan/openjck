import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://agentrace.dev",
  integrations: [
    sitemap(),
    starlight({
      title: "AgentTrace",
      description: "Visual debugger for AI agent loops. Step-by-step. Locally. Zero config.",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/ravaniroshan/agentrace",
        },
      ],
      customCss: ["./src/styles/custom.css"],
      head: [
        {
          tag: "meta",
          attrs: {
            name: "google-site-verification",
            content: "5sngnBez0zAJUjzsGz8WTpoJ6Jybxa5YAFORTOBDKvk"
          },
        },
        {
          tag: "meta",
          attrs: {
            property: "og:image",
            content: "https://agentrace.dev/og.png"
          },
        },
        {
          tag: "meta",
          attrs: {
            property: "og:type",
            content: "website"
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:card",
            content: "summary_large_image"
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:title",
            content: "AgentTrace — Visual debugger for AI agents",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:description",
            content: "Your agent ran 15 steps. Something broke at step 9. AgentTrace shows you exactly what happened.",
          },
        },
        {
          tag: "link",
          attrs: {
            rel: "icon",
            type: "image/svg+xml",
            href: "/favicon.svg"
          },
        },
        {
          tag: "script",
          attrs: {
            type: "application/ld+json"
          },
          content: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            name: "AgentTrace",
            description: "Visual debugger for AI agent loops. Step-by-step. Locally. Zero config.",
            url: "https://agentrace.dev",
            applicationCategory: "DeveloperApplication",
            operatingSystem: "Linux, macOS, Windows",
            offers: {
              "@type": "Offer",
              price: "0",
              priceCurrency: "USD"
            },
            author: {
              "@type": "Person",
              name: "Roshan Ravani"
            },
            codeRepository: "https://github.com/ravaniroshan/agentrace",
            license: "https://opensource.org/licenses/MIT",
            keywords: "AI agents, LLM debugging, agent observability, LangChain debugger",
          }),
        },
      ],
      sidebar: [
        {
          label: "Getting Started",
          items: [
            { label: "Quick Start", slug: "guides/quickstart" },
            { label: "How It Works", slug: "guides/how-it-works" },
            { label: "Installation", slug: "guides/installation" },
          ],
        },
        {
          label: "API Reference",
          items: [
            { label: "@trace", slug: "reference/trace" },
            { label: "@trace_llm", slug: "reference/trace-llm" },
            { label: "@trace_tool", slug: "reference/trace-tool" },
            { label: "EventCapture", slug: "reference/event-capture" },
            { label: "CLI Commands", slug: "reference/cli" },
          ],
        },
        {
          label: "Integrations",
          items: [
            { label: "LangChain", slug: "integrations/langchain" },
            { label: "CrewAI", slug: "integrations/crewai" },
            { label: "Ollama", slug: "integrations/ollama" },
            { label: "OpenAI", slug: "integrations/openai" },
          ],
        },
      ],
    }),
  ],
});
