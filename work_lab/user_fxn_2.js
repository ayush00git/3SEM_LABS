// Write a javascript program to implement user-defined functions
const sumN = (n) => {
    let sum = 0;
    for(let i = 1; i <= n; i++){
        sum += i;
    }
    return sum;
}

const sumOfN = sumN(7);
console.log(`The sum of n terms is ${sumOfN}`);