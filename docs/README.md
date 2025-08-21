# 📚 ClickUp-MCP-Server Documentation

Welcome to the documentation site for ClickUp-MCP-Server! This site is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## 🗂️ Documentation Structure

The documentation is organized into the following sections:

- **📖 Docs** - Main user documentation and guides
- **👨‍💻 Development** - Technical documentation for developers
- **✍️ Blog** - Project updates and technical articles

## 🚀 Getting Started

### 📋 Prerequisites

- [Node.js](https://nodejs.org/) (v16 or higher)
- [pnpm](https://pnpm.io/) (recommended) or npm

### 🛠️ Installation

```bash
# Install dependencies
cd docs
pnpm install
```

### 💻 Local Development

```bash
# Start the development server
pnpm start --no-open
```

This will open a browser window with the documentation site. Most changes are reflected live without having to restart the server.

## 🏗️ Building

```bash
# Build the documentation site
pnpm build
```

This builds the static content into the `build` directory, which can be served using any static hosting service.

## 🧪 Testing the Build

```bash
# Serve the built website locally
pnpm serve --no-open
```

## 📝 Contributing to Documentation

### 📄 Creating New Content

1. Add new Markdown files to:
   - `contents/document/` for user documentation
   - `contents/development/` for developer documentation
   - `contents/blog/` for blog posts

2. Update the appropriate sidebar configuration:
   - `contents/document/sidebars.ts` for docs
   - `contents/development/sidebars.ts` for dev docs

### ✨ Best Practices

- Use clear, concise language
- Include code examples where appropriate
- Add diagrams for complex concepts (Mermaid diagrams are supported)
- Use admonitions for important notes, warnings, etc.

## 🔄 Deployment

Documentation is automatically deployed when changes are merged to the main branch.

## 📘 Additional Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Flavor Markdown](https://github.github.com/gfm/)
