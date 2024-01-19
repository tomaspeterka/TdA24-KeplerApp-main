class SearchDropDown {
    constructor(dropdown, input, options_list, space_submit = false, reset_on_submit = false){
        this.dropdown = dropdown
        this.input = input
        this.key_selected = -1
        this.reset_on_submit = reset_on_submit
        let da_class = this
        setInterval(function () { da_class.search_dropdown_update(); }, 1);
        this.options_div = dropdown.getElementsByTagName("div")[0]
        this.options_div.innerHTML = ""

        this.pseudo_vals = []
        this.used_options = []

        for (let i = 0; i < indexes['locations'].length; i++){
            let option_text = options_list[i]
            let option = document.createElement("a")
            option.tabIndex = 0
            option.className = "option"
            option.innerText = option_text;

            option.addEventListener("click", function (){ da_class.dropdown_option_click(option_text); });

            this.options_div.appendChild(option)


            this.pseudo_vals.push(input_2_pseudo_val(option_text))
        }
        let not_found = document.createElement("div")
        not_found.tabIndex = 0
        not_found.className = "option"
        not_found.innerText = "nic nenalezeno"
        not_found.style.display = "none"
        not_found.style.borderRadius = "0px 0px 8px 8px";
        this.options_div.appendChild(not_found)

        this.reduce_search_options("")

        input.addEventListener("input", function () { da_class.reduce_search_options(da_class.input.value) });

        input.addEventListener("keydown", (event) => {
            if (event.keyCode === 13){
                da_class.pseudo_2_profi()
            } else if (space_submit && event.keyCode === 32) {
                da_class.pseudo_2_profi()
            }
        });

        dropdown.addEventListener("keydown", (event) => {
            if (event.keyCode === 40) {
                da_class.option_key_move(1);
                event.preventDefault()
            } else if(event.keyCode === 38){
                da_class.option_key_move(-1);
                event.preventDefault()
            } else if (event.keyCode === 13 && this.key_selected >= 0){
                da_class.option_key_move(0)
                event.preventDefault()
            }
        })

        this.options_div.addEventListener('transitionend', () => {
            if (this.options_div.style.display === "block" && this.options_div.style.opacity === "0") { this.options_div.style.display = "none" }
        });
    }

    dropdown_option_click(value){
        this.input.value = value
        document.activeElement.blur()
        this.key_selected = -1

        this.input_submit_event()

        if (this.reset_on_submit){
            this.input.value = ""
            this.reduce_search_options("")
            this.input.focus()
        }
        this.search_dropdown_update()
    }

    search_dropdown_update(){
        let last_focused = this.options_div.style.display === "block"
        if (this.options_div.style.opacity < 1) last_focused = false

        let dropdown_focused = this.dropdown.contains(document.activeElement) || document.activeElement === this.dropdown


        if (last_focused && !dropdown_focused) {
            this.pseudo_2_profi()
            this.options_div.style.opacity = 0
        } else if (!last_focused && dropdown_focused){
            this.options_div.style.opacity = 1
            this.options_div.style.display = "block"
        }
    }

    reduce_search_options(search){
        search = input_2_pseudo_val(search)

        let options = this.options_div.getElementsByTagName("a")
        let match_exists = false
        let first = null
        let last = null
        for (let i = 0; i < this.pseudo_vals.length; i++){
            if (this.used_options.length > 0 && this.used_options.indexOf(this.pseudo_vals[i]) !== -1) { options[i].style.display = "none"; continue; }
            let search_match = this.pseudo_vals[i].includes(search)
            options[i].style.display = ["none", "block"][search_match ? 1 : 0]
            if (search_match) {
                if (first === null) first = options[i]
                last = options[i]
                match_exists = true
                options[i].style.borderRadius = "0px";
            }
        }

        if (first !== null){
            last.style.borderRadius = "0px 0px 8px 8px";
        }

        this.options_div.getElementsByTagName("div")[0].style.display = ["none", "block"][!match_exists ? 1 : 0]
    }



    pseudo_2_profi(){
        let options = this.options_div.getElementsByTagName("a")
        let pseudo_val = input_2_pseudo_val(this.dropdown.getElementsByTagName("input")[0].value)

        if (!this.reset_on_submit && pseudo_val === "" && document.activeElement === this.input) {
            this.dropdown_option_click("")
            return
        }

        for (let i = 0; i < options.length; i++){
            if (input_2_pseudo_val(options[i].innerHTML) === pseudo_val){
                this.input.value = options[i].innerHTML;

                if (document.activeElement === this.input){
                    this.dropdown_option_click(this.input.value)
                }
                return
            }
        }
    }

    option_key_move(move_diff){
        this.key_selected += move_diff

        let options = this.options_div.children
        let available_options = []

        for (let i = 0; i < options.length; i++){
            if (options[i].style.display !== "none" && options[i].nodeName === "A"){
                available_options.push(options[i])
            }
        }


        if (this.key_selected < 0 || available_options.length === 0){
            this.key_selected = -1
            document.activeElement.blur()
            this.input.focus();
            return
        }

        if(this.key_selected >= available_options.length){
            this.key_selected = available_options.length - 1
        }

        if (move_diff === 0) {
            this.dropdown_option_click(available_options[this.key_selected].innerHTML);
            return;
        }

        document.activeElement.blur()
        available_options[this.key_selected].focus()
    }

    input_submit_event(){
        const input_submit = new CustomEvent("input_submit", {
            detail: {
                input: this.input.value,
            },
        });
        this.dropdown.dispatchEvent(input_submit)
    }
}

function input_2_pseudo_val(input){
    let pseudo_val = input.toLowerCase()
    pseudo_val = pseudo_val.trim()
    pseudo_val = removeAccents(pseudo_val)
    return pseudo_val
}

const removeAccents = str =>
    str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');


function add_tag_to_tag_list(tag_name, tag_list, dropdown){
    let tag = document.createElement("div")
    tag.innerHTML = tag_name + "<span style='float:right;'>×</span>"
    tag.title = tag_name
    tag.style.opacity = "0";
    tag.addEventListener("click", function () {
        dropdown.used_options.splice(dropdown.used_options.indexOf(input_2_pseudo_val(tag_name)), 1)
        dropdown.reduce_search_options(dropdown.input.value)

        tag.style.opacity = "0";
        tag.addEventListener("transitionend", () => { tag.remove() })
        search_but()
    })

    tag_list.insertBefore(tag, dropdown.dropdown).style.opacity = "1";
}