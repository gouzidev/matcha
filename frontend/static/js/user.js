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

const rad_edit_btns = document.querySelectorAll(".form-radio-edit-btn")

rad_edit_btns.forEach(btn => {
    btn.addEventListener("click", (e) => 
    {
        document.getElementById("male").disabled = ! document.getElementById("male").disabled
        document.getElementById("female").disabled = ! document.getElementById("female").disabled
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

let undo_confirm_btn = document.querySelector(".cancel-delete-user-pic-btn");

undo_confirm_btn.addEventListener("click", (e) => {
    const popup_model = document.querySelector(".popup-modal")
    popup_model.style.display = "none"
    e.preventDefault();
});



let delete_img_btn = document.querySelector(".delete-user-pic-confirm-btn");

delete_img_btn.addEventListener("click", (e) => {
    const popup_model = document.querySelector(".popup-modal")
    popup_model.style.display = "none"
    fetch(`/user/picture/${user.id}`, 
        {method : "DELETE"}
    ).then(res => {
        console.log(res.text())
        window.location.reload()
    }
    ).catch(err => {
        console.error(err)})
});


let tag_delete_icons = document.querySelectorAll(".tag-delete-icon")

tag_delete_icons.forEach(del_icon => {
    del_icon.addEventListener("click", (e) => {
        const target = e.target
        const tag_item = target.parentElement
        const tag_value = tag_item.querySelector(".tag-value")
        console.log(tag_value.dataset);
        
        const tagId = tag_value.dataset.tagId
        const userId = tag_value.dataset.userId

        fetch(`/tag/${userId}/${tagId}`, {method: "DELETE"})
        .then(res => console.log(res.text())).finally(res =>
            window.location.reload()
        )
    })
})