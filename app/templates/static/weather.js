const PREDCIT_CONTAINER = document.querySelector('.prediction-container');
const button = document.getElementById('submit')
var xhr = new XMLHttpRequest();
const searched_before = document.querySelectorAll('.searched-before-item')
const city_title = document.querySelector('.city-title')
const error_message = document.querySelector('.error-message')
var currentDate = new Date()
const baseURL = 'http://localhost:8000'


var input = document.getElementById('user_form');

console.log(currentDate.getDate())


function get_prediction(city_name){
    xhr.open('POST', `${baseURL}/weather/${input.value}`,false)
        xhr.send();
        if (xhr.status == 200){
        return  JSON.parse(xhr.responseText)
    } else {
        return null
    }
    
}

function create_item(date,item_info){
    console.log(item_info)
    return `<div class="item">
                    <div class="item-title-date">${date} </div>
                    <div class="time-container">
                        <div class="time">
                            <span class="morning">Утро - ${parseInt(item_info['morning']['temp'])}°</span>
                            <span>Вероятность осадков - ${parseInt(item_info['morning']['precip_chance'])}%</span>
                            <span>Ветер - ${parseInt(item_info['morning']['wind'])} км/ч</span>
                        </div>
                        <div class="time">
                            <span class="day">День - ${parseInt(item_info['day']['temp'])}°</span>
                            <span>Вероятность осадков - ${parseInt(item_info['day']['precip_chance'])}%</span>
                            <span>Ветер - ${parseInt(item_info['day']['wind'])} км/ч</span>
                        </div>
                        <div class="time">
                            <span class="evening">Вечер - ${parseInt(item_info['evening']['temp'])}°</span>
                            <span>Вероятность осадков - ${parseInt(item_info['evening']['precip_chance'])}%</span>
                            <span>Ветер - ${parseInt(item_info['evening']['wind'])} км/ч</span>
                        </div>
                        <div class="time">
                            <span class="night">Ночь - ${parseInt(item_info['night']['temp'])}°</span>
                            <span>Вероятность осадков - ${parseInt(item_info['night']['precip_chance'])}%</span>
                            <span>Ветер - ${parseInt(item_info['night']['wind'])} км/ч</span>
                        </div>
                    </div></div>`
}

function insert_info(prediction){
    var items_container = document.querySelector('.items-container')
    items_container.innerHTML = ''
    console.log(prediction)
    for (var item in prediction['prediction']){
        items_container.innerHTML += create_item(item ,prediction['prediction'][item])
    }
    PREDCIT_CONTAINER.classList.remove('deactive')

}



button.addEventListener('click', function() {
    console.log(input.value)
    if (input.value){
        error_message.classList.add('deactive')
        var prediction = get_prediction(input.value)
        if (prediction){
            insert_info(prediction)
            city_title.innerHTML = input.value
        } else {
            error_message.classList.remove('deactive')
        }
        
    } else {
        console.log('Пусто')
    }
    
})


searched_before.forEach(el =>{
    el.addEventListener('click', (e) =>{
        let self = e.currentTarget;
        input.value = self.innerHTML
        
    })
})