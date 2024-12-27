document.addEventListener('DOMContentLoaded', () => {
    // Fetch the cart from the server on page load
    fetch('/get-cart')
        .then(response => response.json())
        .then(cart => {
            const cartCountElement = document.getElementById('cart-count');
            console.log('Cart count element:', cartCountElement);
            if (!cartCountElement) {
                console.warn('Cart count element not found in the DOM.');
                return;
            }
            // Sync the client-side cart with the server cart
            updateCartCount(cart);
            updateCartItems(cart);
        })
        .catch(error => {
            console.error('Error fetching cart:', error);
        });

    // Attach event listeners to all "Add to cart" buttons
    const cartButtons = document.querySelectorAll('.add-to-cart-btn');
    cartButtons.forEach(button => {
        button.addEventListener('click', () => {
            const name = button.dataset.name; // Get the product name
            const price = parseFloat(button.dataset.price); // Get the product price
            const image = button.dataset.img; // Get the product's image

            // Call the addToCart function with the product details
            addToCart({ name, price, image });
        });
    });

    // Attach event listener for the checkout button
    const checkoutButton = document.getElementById('btn-checkout');
    if(checkoutButton){
        checkoutButton.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent navigation
            fetch('/session-check')
                .then(response => response.json())
                .then(data => {
                    console.log('Session check response:', data);
                    if(!data.logged_in){
                        console.log('User not logged in, showing login modal.');
                        event.preventDefault();
                        showLoginModal();
                    } else {
                        window.location.href = checkoutButton.href;
                    }
                })
                .catch(error => console.error('Error checking session:', error));
        });
    }

    // Handle login form submission in the modal at checkout page
    const loginForm = document.getElementById('loginForm');
    if(loginForm){
        loginForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Prevent default form submission
            const formData = new FormData(loginForm);
            fetch('login', {
                method: 'POST', body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if(data.success){
                        closeLoginModal();
                        location.reload();
                    } else {
                        alert(data.message || 'Sign in failed, please try again.');
                    }
                })
                .catch(error => console.error('Error logging in:', error));
        });
    }
});

// Function to show the login modal at checkout page
function showLoginModal(){
    console.log('Triggering login modal.');
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

// Function to close the login modal at checkout page
function closeLoginModal(){
    const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
    if(loginModal){
        loginModal.hide();
    }
}

function showLoginModal() {
    const modalElement = document.getElementById('loginModal');
    console.log('Modal element:', modalElement);
    if (!modalElement) {
        console.error('Login modal not found in the DOM.');
        return;
    }
    const loginModal = new bootstrap.Modal(modalElement);
    loginModal.show();
}

// Function to handle adding to the cart
function addToCart(product){
    console.log(`Adding ${product.name} to cart at RM${product.price}`);

    // Send the product to the server using Fetch API
    fetch('/add-to-cart', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ product }),
    })
        .then(response => response.json())
        .then(data => {
            if(data.success){
                console.log('Product successfully added to cart:', data.cart);
                updateCartCount(data.cart);
                updateCartItems(data.cart);
            } else{
                alert('Failed to add the product to the cart.');
            }
        })
        .catch(error => {
            console.error('Error adding product to cart:', error);
        });
}

// Function to update the cart count in the UI
function updateCartCount(cart){
    console.log('Updating cart count...');
    const cartCountElement = document.getElementById('cart-count');
    if(!cartCountElement){
        console.warn(`Cart count element not found in the DOM.`);
        return;
    }

    console.log('Cart element found, updating count.');
    if(!cart || Object.keys(cart).length === 0) {
        cartCountElement.textContent = 0;
        return;
    }
    const count = cart ? Object.values(cart).reduce((total, item) => total + item.quantity, 0) : 0;
    cartCountElement.textContent = count;
}


// Function to update cart items in the UI
function updateCartItems(cart){
    const cartItems = document.getElementById('cart-items');
    const cartItemsTable = document.getElementById('cart-items-table');
    const totalPriceElement = document.getElementById('total-price');
    const checkoutButton = document.getElementById('btn-checkout');
    const viewCartButton = document.getElementById('btn-viewCart');

    let totalPrice = 0;

    if(cartItems){
        cartItems.innerHTML = ''; // Clear existing content
        if(Object.keys(cart).length === 0) {
            cartItems.innerHTML = '<li class="list-group-item text-center">Your cart is empty!</li>';
            checkoutButton.classList.add('d-none');
            viewCartButton.classList.add('d-none');
        } else {
            for(const [name, { price, quantity, image }] of Object.entries(cart)) {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                    <img src="${image}" alt="${name}" class="img-thumbnail" style="width: 60px; height: 60px; object-fit: cover;">
                    <span>${name} (x${quantity})</span>
                    <span>RM${(price * quantity).toFixed(2)}</span>
                `;

                const removeButton = document.createElement('button');
                removeButton.className = 'btn btn-danger btn-sm ms-2';
                removeButton.textContent = 'Remove';
                removeButton.dataset.name = name;
                removeButton.addEventListener('click', () => {
                    removeFromCart(name);
                });

                listItem.appendChild(removeButton);
                cartItems.appendChild(listItem);

                totalPrice += price * quantity;
            }

            checkoutButton.classList.remove('d-none');
            viewCartButton.classList.remove('d-none');
        }
    }

    if(cartItemsTable){
        cartItemsTable.innerHTML = ''; // Clear existing content
        if(Object.keys(cart).length === 0) {
            cartItemsTable.innerHTML = '<tr><td colspan="5" class="text-center">Your cart is empty!</td></tr>';
            // checkoutButton.classList.add('d-none');
        } else {
            for(const [name, { price, quantity }] of Object.entries(cart)) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${name}</td>
                    <td>RM${price.toFixed(2)}</td>
                    <td>${quantity}</td>
                    <td>RM${(price * quantity).toFixed(2)}</td>
                    <td><button class="btn btn-danger btn-sm remove-from-cart-btn" data-name="${name}">Remove</button></td>
                `;

                const removeButton = row.querySelector('.remove-from-cart-btn');
                removeButton.addEventListener('click', () => {
                    removeFromCart(name);
                });

                cartItemsTable.appendChild(row);

                totalPrice += price * quantity;
            }

            // checkoutButton.classList.add('d-none');
        }
    }

    if(totalPriceElement){
        totalPriceElement.textContent = `RM${totalPrice.toFixed(2)}`;
    }
}

function updateCheckoutCart(cart){
    const cartItemsElement = document.getElementById('cart-items');
    const totalPriceElement = document.getElementById('total-price');

    let totalPrice = 0;
    cartItemsElement.innerHTML = '';

    if(Object.keys(cart).length === 0){
        cartItemsElement.innerHTML = '<li class="list-group-item">Your cart is empty!</li>';
    } else {
        for (const [name, { price, quantity, image }] of Object.entries(cart)) {
            const listItem = document.createElement('div');
            listItem.className = 'd-flex justify-content-between mb-2';
            listItem.innerHTML = `
                <div>
                    <img src="${image}" alt="${name}" class="img-thumbnail"
                         style="width: 60px; height: 60px; object-fit: cover;">
                    <span>${name} (x${quantity})</span>
                </div>
                <span>RM${(price * quantity).toFixed(2)}</span>
            `;

            cartItemsElement.appendChild(listItem);
            totalPrice += price * quantity;
        }
    }

    totalPriceElement.textContent = `RM${totalPrice.toFixed(2)}`;
}

function removeFromCart(name){
    console.log(`Removing ${name} from cart`);

    fetch('/remove-from-cart', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name }),
    })
        .then(response => response.json())
        .then(data => {
            if(data.success){
                console.log(`${name} removed from cart.`);
                updateCartCount(data.cart);
                updateCartItems(data.cart);
            } else{
                alert('Failed to remove the product from the cart.');
            }
        })
        .catch(error => {
            console.error('Error removing product from cart:', error);
        });
}