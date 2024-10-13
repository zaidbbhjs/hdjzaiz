// static/js/validate.js

function validateForm() {
    let errors = [];
    
    const name = document.getElementById("name").value;
    const cardNumber = document.getElementById("card_number").value;
    const cvv = document.getElementById("cvv").value;
    const expMonth = document.getElementById("exp_month").value;
    const expYear = document.getElementById("exp_year").value;
    
    if (!name || !cardNumber || !cvv || !expMonth || !expYear) {
        errors.push("All fields are required.");
    }
    if (cardNumber.length !== 16) {
        errors.push("Card number must be 16 digits.");
    }
    if (cvv.length !== 3) {
        errors.push("CVV must be 3 digits.");
    }
    
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1;
    const expDate = new Date(expYear, expMonth - 1);
    if (errors.length > 0) {
        const errorList = document.getElementById("error-list");
        errorList.innerHTML = '';
        errors.forEach(error => {
            const li = document.createElement("li");
            li.textContent = error;
            errorList.appendChild(li);
        });
        return false;
    }

    return true;
}
