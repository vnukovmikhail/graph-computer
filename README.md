```mermaid
flowchart TD
  A[User opens dashboard] --> B{Need fresh diagram?}
  B -->|Yes| C[Beautify Mermaid source]
  B -->|No| D[Load last export]
  C --> E[Preview SVG]
  E --> F[Export PNG]
  D --> F
```
