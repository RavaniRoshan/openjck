import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://openjck.dev",
  integrations: [
    sitemap(),
    starlight({
      title: "OpenJCK",
      description: "Visual debugger for AI agent loops. Step-by-step. Locally. Zero config.",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/RavaniRoshan/openjck",
        },
      ],
      customCss: ["./src/styles/custom.css"],
      head: [
        {
          tag: "link",
          attrs: { rel: "preconnect", href: "https://fonts.googleapis.com" }
        },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Syne:wght@400;600;700;800&display=swap"
          }
        },
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
            content: "https://openjck.dev/og.png"
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
            content: "OpenJCK — Visual debugger for AI agents",
          },
        },
        {
          tag: "meta",
          attrs: {
            name: "twitter:description",
            content: "Your agent ran 15 steps. Something broke at step 9. OpenJCK shows you exactly what happened.",
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
            name: "OpenJCK",
            description: "Visual debugger for AI agent loops. Step-by-step. Locally. Zero config.",
            url: "https://openjck.dev",
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
            codeRepository: "https://github.com/RavaniRoshan/openjck",
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
            { label: "Dashboard", slug: "guides/dashboard" },
            { label: "Failure Intelligence", slug: "guides/failure-intelligence" },
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
