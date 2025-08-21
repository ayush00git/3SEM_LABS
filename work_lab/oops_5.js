class Organization {

    constructor(name, cap){
        this.name = name;
        this.cap = cap;
    }
    
    org(){
        console.log(`Parent company: ${this.name} with a market cap of ${this.cap}`);
    }

    // encapsulation
    #secrets = 'The company is stealing some data and selling it to government';

    // polymorphism
    emp() {
        console.log(`A total of 10k employees`);
    }
}
// Inheritance
class Company extends Organization {
    ceo = "Larry";

    constructor(name, cap, product){
        super(name, cap);
        this.product = product;
    }

    brand(){
        console.log(`The parent company ${this.name} with a market cap of ${this.cap} and the brand product as ${this.product}`);
    }
    
    // polymorphism
    emp() {
        console.log(`A total of 1k employees`);
    }
}

// const head = new Organization("Alphabet", "1T");
// head.org();

const prod = new Company("Google", "$50B", "YouTube");
// console.log(prod.#secrets);      // will throw an error because the secrets field is a private field and cant be accessed outside the class
prod.brand();
prod.emp();
