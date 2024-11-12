const icons = document.querySelectorAll(".password-visibility-icon")

icons.forEach(icon => {
    icon.addEventListener("click", (e) => {
        const icon = e.target
        const parent = icon.parentElement
        const input = parent.querySelector(".form-input")
    
        if (input.type == "text")
        {
            input.type = "password"
            icon.style["opacity"] = 1
        }
        else
        {
            input.type = "text"
            icon.style["opacity"] = 0.5
    
        }
    })
})
