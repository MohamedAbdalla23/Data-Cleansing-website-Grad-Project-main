let container = document.getElementById('container');

toggle = () => {
    container.classList.toggle('sign-in');
    container.classList.toggle('sign-up');
}

setTimeout(() => {
    container.classList.add('sign-in');
}, 200);

function validateSignUp() {
    const name = document.getElementById("nameInput").value;
    const username = document.getElementById("usernameInput").value;
    const email = document.getElementById("emailInput").value;
    const password = document.getElementById("passwordInput").value;
    const confirmPassword = document.getElementById("confirmPasswordInput").value;

    const nameRegex = /^[A-Za-z]{3,}$/;
    const usernameRegex = /^[A-Za-z][A-Za-z0-9]*$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^.{6,}$/;

    if (!nameRegex.test(name)) {
        document.getElementById("nameError").innerText = "Name must be at least 3 characters long.";
    } else {
        document.getElementById("nameError").innerText = "";
    }
    if (!usernameRegex.test(username)) {
        document.getElementById("usernameError").innerText = "Username must not start with a number and must contain only letters and numbers.";
    } else {
        document.getElementById("usernameError").innerText = "";
    }
    if (!emailRegex.test(email)) {
        document.getElementById("emailError").innerText = "Invalid email address format.";
    } else {
        document.getElementById("emailError").innerText = "";
    }
    if (!passwordRegex.test(password)) {
        document.getElementById("passwordError").innerText = "Password must be at least 6 characters long.";
    } else {
        document.getElementById("passwordError").innerText = "";
    }
    if (password !== confirmPassword) {
        document.getElementById("confirmPasswordError").innerText = "Passwords do not match.";
    } else {
        document.getElementById("confirmPasswordError").innerText = "";
    }
}

function submitSignUp() {
    let users = JSON.parse(localStorage.getItem('users')) || [];

    const name = document.getElementById("nameInput").value;
    const username = document.getElementById("usernameInput").value;
    const email = document.getElementById("emailInput").value;
    const password = document.getElementById("passwordInput").value;
    const confirmPassword = document.getElementById("confirmPasswordInput").value;

    const nameRegex = /^[A-Za-z]{3,}$/;
    const usernameRegex = /^[A-Za-z][A-Za-z0-9]*$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^.{6,}$/;

    if (!nameRegex.test(name)) {
        document.getElementById("nameError").innerText = "Name must be at least 3 characters long.";
        return;
    }
    if (!usernameRegex.test(username)) {
        document.getElementById("usernameError").innerText = "Username must not start with a number and must contain only letters and numbers.";
        return;
    }
    if (!emailRegex.test(email)) {
        document.getElementById("emailError").innerText = "Invalid email address format.";
        return;
    }
    if (!passwordRegex.test(password)) {
        document.getElementById("passwordError").innerText = "Password must be at least 6 characters long.";
        return;
    }
    if (password !== confirmPassword) {
        document.getElementById("confirmPasswordError").innerText = "Passwords do not match.";
        return;
    }

    const emailExists = users.some(user => user.email === email);
    if (emailExists) {
        document.getElementById("emailError").innerText = "Email already exists.";
        return;
    }

    const newUser = { name, username, email, password };
    users.push(newUser);
    localStorage.setItem('users', JSON.stringify(users));

    document.getElementById("errorMessage").classList.remove("danger");
    document.getElementById("errorMessage").classList.add("success");
    document.getElementById("errorMessage").innerText = "Success! User is saved.";

    document.getElementById("nameInput").value = "";
    document.getElementById("usernameInput").value = "";
    document.getElementById("emailInput").value = "";
    document.getElementById("passwordInput").value = "";
    document.getElementById("confirmPasswordInput").value = "";
}

function validateSignIn() {
    const signInEmail = document.getElementById("signInEmailInput").value;
    const signInPassword = document.getElementById("signInPasswordInput").value;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const passwordRegex = /^.{6,}$/;

    if (!emailRegex.test(signInEmail)) {
        document.getElementById("signInEmailError").innerText = "Invalid email address format.";
    } else {
        document.getElementById("signInEmailError").innerText = "";
    }

    if (!passwordRegex.test(signInPassword)) {
        document.getElementById("signInPasswordError").innerText = "Password must be at least 6 characters long.";
} else {
document.getElementById("signInPasswordError").innerText = "";
}
}

function submitSignIn() {
	const signInEmail = document.getElementById("signInEmailInput").value;
	const signInPassword = document.getElementById("signInPasswordInput").value;
	const users = JSON.parse(localStorage.getItem('users')) || [];
  
	if (!users || users.length === 0) {
	  document.getElementById("signInErrorMessage").classList.remove("success");
	  document.getElementById("signInErrorMessage").classList.add("danger");
	  document.getElementById("signInErrorMessage").innerText = "No users found.";
	  return;
	}
  
	const matchedUser = users.find(user => user.email === signInEmail && user.password === signInPassword);
  
	if (matchedUser) {
	  document.getElementById("signInErrorMessage").classList.remove("danger");
	  document.getElementById("signInErrorMessage").classList.add("success");
	  document.getElementById("signInErrorMessage").innerText = "Success! Logged in.";
	  localStorage.setItem('user', JSON.stringify(matchedUser));
	  window.location.href = "/home"; // Replace "/home" with your actual home page URL
	} else {
	  document.getElementById("signInErrorMessage").classList.remove("success");
	  document.getElementById("signInErrorMessage").classList.add("danger");
	  document.getElementById("signInErrorMessage").innerText = "Incorrect email or password.";
	}
  }
  


