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


// document.addEventListener("DOMContentLoaded", () => {
//     let show_img_btn = document.querySelector(".show-img-btn");

//     show_img_btn.addEventListener("click", (e) => {
//         e.preventDefault();
//         fetch(`/profile/picture/${user.id}`, {
//             method: "GET"
//         })
//         .then(res => res.text())
//         .then(html => {
//             // Open a new window or tab to display the image
//             let newWindow = window.open();
//             newWindow.document.write(html);
//         })
//         .catch(err => console.error(err));
//     });
// });