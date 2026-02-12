# Questions Your MCP Tools Can Answer

This guide provides example questions that each MCP tool is optimized to answer, helping you get the most value from your Codebase Intelligence server.

---

## 1. 🔍 index_codebase

**Purpose**: Index your codebase for intelligent analysis and semantic search.

### Best Questions:
- "Can you index my entire project so I can search through it?"
- "I want to analyze my codebase - can you index all Python files?"
- "Index my src directory excluding test files and cache folders"
- "Prepare my codebase for semantic search and analysis"
- "Index only JavaScript and TypeScript files in my project"
- "How many files and code chunks are in my codebase?"
- "Re-index my project after making major changes"

### Use Cases:
- Initial project setup for code intelligence
- After major refactoring or adding new features
- When you want to enable semantic search
- Before running other analysis tools

---

## 2. 🔎 semantic_search

**Purpose**: Search code by meaning and intent, not just keywords.

### Best Questions:
- "Find all code related to database connections"
- "Where do we handle user authentication?"
- "Show me code that deals with file uploads"
- "Find functions that process payment transactions"
- "Where is error handling implemented?"
- "Show me all API endpoint definitions"
- "Find code that uses machine learning models"
- "Where do we validate user input?"
- "Show me caching implementations"
- "Find all async/await patterns in the code"
- "Where do we handle WebSocket connections?"
- "Show me code related to email sending"

### Use Cases:
- Understanding unfamiliar codebases
- Finding similar implementations
- Locating specific functionality
- Code review and discovery
- Refactoring preparation

---

## 3. 📊 compute_metrics

**Purpose**: Calculate code quality, complexity, and maintainability metrics.

### Best Questions:
- "What's the code quality of my project?"
- "Which files have the highest complexity?"
- "What's the maintainability index of this module?"
- "Show me complexity metrics for the entire codebase"
- "Which functions are too complex and need refactoring?"
- "What's the average cyclomatic complexity?"
- "How many lines of code vs comments do I have?"
- "Which files have low maintainability scores?"
- "What's the Halstead complexity of this file?"
- "Show me technical debt indicators"
- "Which modules need the most attention?"

### Use Cases:
- Code quality assessment
- Identifying refactoring candidates
- Technical debt tracking
- Code review preparation
- Setting quality benchmarks

---

## 4. 🔄 detect_duplicates

**Purpose**: Find duplicate and similar code across your codebase.

### Best Questions:
- "Are there any duplicate code blocks in my project?"
- "Find similar implementations across different files"
- "Which code is copy-pasted and should be refactored?"
- "Show me code duplication with 90% similarity"
- "Where can I extract common functions?"
- "Find repeated patterns that could be abstracted"
- "Which files have similar logic?"
- "Show me candidates for DRY refactoring"
- "Are there duplicate utility functions?"
- "Find similar error handling code"

### Use Cases:
- DRY principle enforcement
- Refactoring opportunities
- Code consolidation
- Reducing maintenance burden
- Improving code reusability

---

## 5. 🕸️ analyze_dependencies

**Purpose**: Analyze module dependencies and detect circular dependencies.

### Best Questions:
- "Show me the dependency graph of my project"
- "Are there any circular dependencies?"
- "Which modules are most tightly coupled?"
- "What does this file depend on?"
- "Show me all imports and dependencies"
- "Which modules have the most dependencies?"
- "Find dependency cycles in my code"
- "What's the dependency depth of this module?"
- "Which files import this module?"
- "Show me the import structure"
- "Are there any isolated modules?"
- "What's the coupling between these components?"

### Use Cases:
- Architecture review
- Refactoring planning
- Identifying tight coupling
- Breaking circular dependencies
- Understanding module relationships

---

## 6. 📝 generate_docs

**Purpose**: Auto-generate documentation from code structure and docstrings.

### Best Questions:
- "Generate documentation for this file"
- "Create API documentation for my project"
- "Document all classes and functions in this module"
- "Generate markdown docs for the entire codebase"
- "What functions and classes are in this file?"
- "Create HTML documentation"
- "Document the public API"
- "Generate a function reference"
- "What are all the dependencies of this module?"
- "Create documentation with examples"

### Use Cases:
- API documentation
- Onboarding new developers
- Code review preparation
- Maintaining up-to-date docs
- Understanding code structure

---

## 7. 💡 suggest_refactorings

**Purpose**: Get AI-powered suggestions for code improvements.

### Best Questions:
- "What refactorings would improve this code?"
- "How can I improve the quality of this file?"
- "Which functions are too long?"
- "What code smells exist in this module?"
- "Suggest improvements for maintainability"
- "Which classes have too many responsibilities?"
- "What can I do to reduce complexity?"
- "Are there any anti-patterns in this code?"
- "How can I make this more testable?"
- "What SOLID principles are violated?"

### Use Cases:
- Code review
- Technical debt reduction
- Quality improvement
- Learning best practices
- Refactoring planning

---

## 8. 💬 ask_codebase

**Purpose**: Ask natural language questions about your codebase.

### Best Questions:
- "What does this codebase do?"
- "How does the authentication system work?"
- "What storage backends are supported?"
- "Explain the main architecture and components"
- "How is data validated in this project?"
- "What design patterns are used?"
- "How does the caching layer work?"
- "What APIs does this project expose?"
- "How is error handling implemented?"
- "What testing frameworks are used?"
- "How does the deployment process work?"
- "What are the main entry points?"
- "How is configuration managed?"
- "What external services does this integrate with?"
- "How is logging implemented?"

### Use Cases:
- Understanding new codebases
- Onboarding documentation
- Architecture exploration
- Feature discovery
- Code comprehension

---

## 9. 📞 get_call_graph

**Purpose**: Generate function call graphs showing relationships.

### Best Questions:
- "Show me the call graph for this function"
- "What functions does this call?"
- "What's the call hierarchy?"
- "Which functions call this function?"
- "Show me the execution flow"
- "What's the call depth of this function?"
- "Map out the function dependencies"
- "Show me the call chain"
- "What's the execution path?"
- "Which functions are called recursively?"

### Use Cases:
- Understanding execution flow
- Debugging complex logic
- Impact analysis
- Refactoring planning
- Performance optimization

---

## 10. 🔍 find_symbol

**Purpose**: Find symbol definitions and usages across the codebase.

### Best Questions:
- "Where is the User class defined?"
- "Find all occurrences of the authenticate function"
- "Where is this variable declared?"
- "Show me all usages of this class"
- "Find the definition of this function"
- "Where is this constant defined?"
- "Show me all references to this symbol"
- "Find the implementation of this interface"
- "Where is this type defined?"
- "Show me all imports of this module"

### Use Cases:
- Code navigation
- Refactoring preparation
- Understanding code usage
- Finding definitions
- Impact analysis

---

## 🎯 Example Workflows

### Workflow 1: Understanding a New Codebase
1. **index_codebase**: Index the entire project
2. **ask_codebase**: "What does this codebase do?"
3. **analyze_dependencies**: Check the architecture
4. **compute_metrics**: Assess code quality
5. **semantic_search**: Find specific features

### Workflow 2: Refactoring Preparation
1. **compute_metrics**: Identify high-complexity files
2. **detect_duplicates**: Find code to consolidate
3. **suggest_refactorings**: Get improvement suggestions
4. **analyze_dependencies**: Check coupling
5. **get_call_graph**: Understand impact

### Workflow 3: Code Review
1. **compute_metrics**: Check quality metrics
2. **suggest_refactorings**: Find issues
3. **detect_duplicates**: Ensure DRY
4. **analyze_dependencies**: Check for circular deps
5. **generate_docs**: Verify documentation

### Workflow 4: Feature Discovery
1. **semantic_search**: "Find authentication code"
2. **find_symbol**: Locate specific classes
3. **get_call_graph**: Understand execution flow
4. **ask_codebase**: "How does auth work?"

### Workflow 5: Quality Improvement
1. **compute_metrics**: Baseline quality
2. **detect_duplicates**: Find duplication
3. **suggest_refactorings**: Get suggestions
4. **analyze_dependencies**: Check coupling
5. **compute_metrics**: Measure improvement

---

## 💡 Pro Tips

### For Best Results:
- **Be Specific**: "Find authentication code" is better than "find code"
- **Use Context**: Mention file names, modules, or features
- **Combine Tools**: Use multiple tools for comprehensive analysis
- **Iterate**: Refine your questions based on results
- **Index First**: Always index before using search/analysis tools

### Question Patterns That Work Well:
- "Show me..." - For discovery
- "Where is..." - For location
- "How does..." - For understanding
- "What..." - For information
- "Find..." - For search
- "Which..." - For comparison
- "Suggest..." - For improvements

### Avoid:
- Vague questions without context
- Questions about code not in the indexed codebase
- Asking for code generation (these tools analyze, not generate)
- Questions requiring external knowledge

---

## 🚀 Getting Started

1. **Index your codebase first**:
   ```
   index_codebase(path="src", languages=["python"])
   ```

2. **Start with broad questions**:
   ```
   ask_codebase("What does this codebase do?")
   ```

3. **Drill down with specific tools**:
   ```
   semantic_search("authentication")
   find_symbol("User", type="class")
   ```

4. **Analyze quality**:
   ```
   compute_metrics("src")
   detect_duplicates("src")
   ```

5. **Get improvements**:
   ```
   suggest_refactorings("src/main.py")
   ```

---

## 📚 Additional Resources

- Check the main `README.md` for setup instructions

---

**Happy Coding! 🎉**

Your MCP tools are ready to help you understand, analyze, and improve your codebase.
