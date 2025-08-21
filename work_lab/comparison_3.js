// 3. Write a javascript program to implement Comparisons and Control Flow
// grading system
// 85 - 100 (A)
// 75 - 85 (B)
// 60 - 75 (C)
// 35 - 60 (E)
// rest F

const marks = 87;

if(marks > 100 || marks < 0){
    console.log(`Not a valid input\nInput marks bw 0 to 100`);
}else if(marks <= 100 && marks > 85){
    console.log(`Grade A`);
}else if(marks > 75 && marks <= 85){
    console.log(`Grade B`);
}else if(marks > 60 && marks <= 75){
    console.log(`Grade C`);
}else if(marks > 35 && marks <= 60){
    console.log(`Grade C`);
}else if(marks < 35){
    console.log(`Fail`)
}