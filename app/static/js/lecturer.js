import QrCreator from 'https://cdn.jsdelivr.net/npm/qr-creator/dist/qr-creator.es6.min.js';
console.log(data);


const name_ele = document.getElementById('whole_name');
name_ele.textContent = data.title_before + ' '  + data.first_name + ' ' + data.middle_name + ' ' + data.last_name + ' ' + data.title_after;

const claim_ele = document.getElementById('claim');
claim_ele.textContent = data.claim;

const img_ele = document.getElementById('profile_image');
img_ele.setAttribute('src', data.picture_url);

const location_ele = document.getElementById('location');
location_ele.textContent = data.location;

const price_ele = document.getElementById('price');
price_ele.textContent = data.price_per_hour;

const paragraph_ele = document.getElementById('paragraph');
paragraph_ele.innerHTML = data.bio;


// const hello = ["111 111 111", "222 222 222", "333 333 333"];
const phone_box = document.getElementById('phone_box');
const email_box = document.getElementById('email_box');

for (let i=0; i<data.contact.telephone_numbers.length; i++) {
    const h3 = document.createElement("h3");
    h3.setAttribute("class", "phone_number");
    h3.textContent = data.contact.telephone_numbers[i];
    phone_box.appendChild(h3);
}

for (let i=0; i<data.contact.emails.length; i++) {
    const h3 = document.createElement("h3");
    h3.setAttribute("class", "email");
    h3.textContent = data.contact.emails[i];
    email_box.appendChild(h3);
}


let emails = [];
for (let i=0; i < data.contact.emails.length; i++)   {
    emails += '\nEMAIL:' + data.contact.emails[i];
}

let phone_nums = [];
for (let i=0; i < data.contact.telephone_numbers.length; i++)   {
    phone_nums += '\nTEL:' + data.contact.telephone_numbers[i];
}

const qrContent = 
'BEGIN:VCARD' + 
'\nVERSION:4.0' + 
'\nFN:' + data.first_name + ' ' + data.last_name + 
'\nN:' + data.last_name + ';' + data.first_name + ';' + data.middle_name + ';' + data.title_before + ';' + data.title_after +
emails + phone_nums +
// '\nPHOTO;ENCODING=BASE64;TYPE=JPEG:[base64-data]' + 
'\nEND:VCARD'


QrCreator.render({
    text: qrContent,
    radius: 0.5, // 0.0 to 0.5
    ecLevel: 'M', // L, M, Q, H
    fill: '#536DFE', // foreground color
    background: null, // color or null for transparent
    size: 400 // in pixels
  }, document.querySelector('#qrcode'));
