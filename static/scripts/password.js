function showPassword(){

    let fieldType = document.getElementById("pin-1").type
    let pin1 = document.getElementById("pin-1")
    let pin2 = document.getElementById("pin-2")
    let pin3 = document.getElementById("pin-3")
    let pin4 = document.getElementById("pin-4")
    let pin5 = document.getElementById("pin-5")
    let pin6 = document.getElementById("pin-6")

    if(fieldType==="password"){

        pin1.type="text"
        pin2.type="text"
        pin3.type="text"
        pin4.type="text"
        pin5.type="text"
        pin6.type="text"

    }

    else{

        pin1.type="password"
        pin2.type="password"
        pin3.type="password"
        pin4.type="password"
        pin5.type="password"
        pin6.type="password"

    }

}