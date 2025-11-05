// 4. Write a javascript program to implement Built in Functions & Methods.

// Global functions
console.log(parseInt(90.564));

console.log(parseFloat(8.23));

console.log(isNaN('ayu'));
console.log(isNaN(987.1));
console.log(isNaN(true));


// array methods
const arr = [1, 4, 6, 7, 8, 10];
const rem = arr.pop();
console.log(rem);

arr.push(7);  // inserts 7 at the end of the array
console.log(arr[5]);

const first = arr.shift();     // removes the first element from the array and return it as well
console.log(first);

console.log(arr.unshift(4));     // inserts 4 to the beginning of the array

console.log(arr.join(''));


// String methods
const str = 'laPtop';
console.log(str.toLowerCase());
console.log(str.toUpperCase());
console.log(str.indexOf("P"));

const st = ' aowl   ';
console.log(st.trim());
console.log(st.replace('a', ''));
console.log(st.charAt("3"));