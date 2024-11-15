document.addEventListener("DOMContentLoaded", (e) => 
{
    let cards = document.querySelectorAll(".user-card")

    cards.forEach(card => {
        card.addEventListener("click", (e) => {
            if (!e.target.classList.contains("card-btns") && !e.target.classList.contains("card-btn"))
            {
                let target = e.target.closest(".user-card")
                const user_id = target.dataset.userId
                console.log(user_id);
                window.location.href = `/user/${user_id}`
            }

        })
    });
})