function generateSMDEConfig(id) {
    return {
        element: document.getElementById(id),
        toolbar: ["bold", "italic", "heading-1", "heading-2", "heading-3", "|", "quote", "unordered-list", "ordered-list", "|", "link", "image", "table", "horizontal-rule", "|", "side-by-side", "fullscreen", "guide"],
        spellChecker: false,
        status: false
    }
}