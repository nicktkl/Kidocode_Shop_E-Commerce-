document.getElementById('p_category').addEventListener('change', function () {
    var categoryId = this.value;
    var subcategorySelect = document.getElementById('p_subcategory');
    
    subcategorySelect.disabled = false;
    subcategorySelect.innerHTML = '<option disabled selected>Select subcategory</option>';
    
    fetch(`/admin/get_subcategories/${categoryId}`)
        .then(response => response.json())
        .then(data => {
            data.subcategories.forEach(subcategory => {
                var option = document.createElement('option');
                option.value = subcategory.categoryID;
                option.text = subcategory.name;
                subcategorySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching subcategories:', error);
        });
});