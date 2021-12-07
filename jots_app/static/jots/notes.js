// Start with first post
let counter = 30;

// Load posts 20 at a time
const quantity = 30;

// When DOM loads, render the first 20 posts
// document.addEventListener('DOMContentLoaded', load);

// If scrolled to bottom, load the next 20 posts
window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        load();
    }
};


// practice

function getToken() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrftoken=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}


// WE ARE HERE
function practice() {
    // token defined on html page
    // collectionId defined on html page
    fetch('/notes_get', {
        method: 'POST',
        headers: { "X-CSRFToken": csrfToken, "collectionId": collectionId },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.notes[0]["text"]);
    })
}

// Load next set of posts
function load() {

    // Set start and end post numbers, and update counter
    const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;

    // Get new posts and add posts
    fetch(`/notes_get?start=${start}&end=${end}`)
    .then(response => response.json())
    .then(data => {
        data.posts.forEach(add_note);
    })
};

// Add a new post with given contents to DOM
function add_note(contents) {

    // Create new post
    const post = document.createElement('div');
    post.className = 'post';
    post.innerHTML = contents;

    // Add post to DOM
    document.querySelector('body').append(post);
};