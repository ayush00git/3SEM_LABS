class Car {
    constructor(brand, year) {
        this.brand = brand
        this.year = year
    }

    display() {
        console.log(`${this.brand} - ${this.year}`)
    }
}

let c1 = new Car("BMW", 2029)
c1.display()