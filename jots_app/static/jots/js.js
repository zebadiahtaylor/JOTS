// js for jots

function showPWandConfirmation() {
    var x = document.getElementById("password");
    var y = document.getElementById("confirmation");
    if (x.type === "password") {
        x.type = "text";
        y.type = "text";
    } else {
        x.type = "password";
        y.type = "password";
    }
    }

function togglePassword() {
    var x = document.getElementById("password");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}

function showDelete($deleteID) {
        
    let deleteform = document.getElementById($deleteID);
    let showBut = document.getElementById(showDel);

    if (showBut.innerText === 'Delete Article?') {
        showBut.innerText = 'Hide Delete Options';
        document.getElementById(`noteForm${$noteId}`).style.display = '';
        document.getElementById('id_for_text').value = document.getElementById('note' + $noteId).innerHTML; 
        document.getElementById('id_for_text').focus()
    }
    else {
        edit.innerText='Edit';
        document.getElementById(`noteForm${$noteId}`).style.display = 'none';
    }
}

function copyNote($noteId) {
    /* Get the text field */
    const copyText = document.getElementById(`note${$noteId}`);
    copyText.focus();
    /* Select the text field */
    copyText[0].select();
    copyText[0].setSelectionRange(0, 99999); /* For mobile devices */
  
     /* Copy the text inside the text field */
    navigator.clipboard.writeText(copyText.value);
  
    /* Alert the copied text */
    alert("Copied the text: " + copyText.value);
}

function editText($noteId) {
        
    let edit = document.getElementById($noteId);
    let noteForm = document.getElementById(`noteForm${$noteId}`);

    if (edit.innerText === 'Edit') {
        hideEditForms();
        edit.innerText = 'nevermind!';
        noteForm.style.display = '';
        populateEditForms($noteId);  
        findFocus();
    }
    else {
        edit.innerText='Edit';
        noteForm.style.display = 'none';
    }
}

function editTextOnNotesAll($noteId) {
        
    let edit = document.getElementById($noteId);
    let noteForm = document.getElementById(`noteForm${$noteId}`);

    if (edit.innerText === 'Edit') {
        hideEditForms();
        edit.innerText = 'nevermind!';
        noteForm.style.display = '';
        populateEditFormsOnNotesAll($noteId);  
        findFocus();
    }
    else {
        edit.innerText='Edit';
        noteForm.style.display = 'none';
    }
}


function hideEditForms() {
    let editButtons = document.getElementsByClassName("editBtn");
    for(var i = 0; i < editButtons.length; i++){
        editButtons[i].innerText = 'Edit';
    }
    let noteForms = document.getElementsByClassName("noteForm");
    for(var i = 0; i < noteForms.length; i++){
        noteForms[i].style.display = 'none';
    }
}

function populateEditForms($noteId) {
    let editForms = document.getElementsByName('text');
    for(var i = 1; i < editForms.length; i++){
        editForms[i].value = document.getElementById('note' + $noteId).innerHTML;
    }
}

function populateEditFormsOnNotesAll($noteId) {
    let editForms = document.getElementsByName('text');
    for(var i = 0; i < editForms.length; i++){
        editForms[i].value = document.getElementById('note' + $noteId).innerHTML;
    }
}

function findFocus() {
    let editForms = document.getElementsByName('text');
    for(var i = 1; i < editForms.length; i++){
        if (editForms[i].style.display === '') {
            editForms[i].focus();
        }
    }
}