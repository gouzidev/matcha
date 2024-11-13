const input_edit_btns = document.querySelectorAll(".form-input-edit-btn")

console.log(input_edit_btns)

input_edit_btns.forEach(btn => {
    btn.addEventListener("click", (e) => 
    {
        const curr_btn = e.target
        const parent   = curr_btn.parentElement
        const input = parent.querySelector(".form-input")
        if (input)
        {
            input.readOnly = !input.readOnly
            input.focus()
        }
    })
})

const rad_edit_btns = document.querySelectorAll(".form-input-edit-btn")

rad_edit_btns.forEach(btn => {
    btn.addEventListener("click", (e) => 
    {
        console.log(document.getElementById("male").disabled);
        document.getElementById("male").disabled = false
        document.getElementById("female").disabled = false
    })
})

document.getElementById("male").addEventListener("change", (e) => {
    document.getElementById("hidden-male").disabled = !e.target.checked;
    document.getElementById("hidden-female").disabled = e.target.checked;
});

document.getElementById("female").addEventListener("change", (e) => {
    document.getElementById("hidden-female").disabled = !e.target.checked;
    document.getElementById("hidden-male").disabled = e.target.checked;
});


let show_delete_popup_img_btn = document.querySelector(".show-delete-popup-btn");

show_delete_popup_img_btn.addEventListener("click", (e) => {
    const popup_model = document.querySelector(".popup-modal")
    popup_model.style.display = "inherit"
});

let undo_confirm_btn = document.querySelector(".cancel-delete-profile-pic-btn");

undo_confirm_btn.addEventListener("click", (e) => {
    const popup_model = document.querySelector(".popup-modal")
    popup_model.style.display = "none"
    e.preventDefault();
});



let delete_img_btn = document.querySelector(".delete-profile-pic-confirm-btn");

delete_img_btn.addEventListener("click", (e) => {
    const popup_model = document.querySelector(".popup-modal")
    popup_model.style.display = "none"
    fetch(`/profile/picture/${user.id}`, 
        {method : "DELETE"}
    ).then(res => {
        console.log(res.text())
        window.location.reload()
    }
    ).catch(err => {
        console.error(err)})
});
