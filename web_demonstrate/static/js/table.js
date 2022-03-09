var tbody =document.querySelector('#prior1')        //左半邊
for(var i = 0 ; i < data1.length ; i++){
    var tr = document.createElement('tr');
    tbody.appendChild(tr);
    for (var k in data1[i] ){
        var td = document.createElement("td");
        td.style.width = "15%";
        td.style.textAlign = "center";
        td.innerText = data1[i][k];
        tr.appendChild(td);
    }
}

var tbody =document.querySelector('#prior2')        //右半邊
for(var i = 0 ; i < data2.length ; i++){
    var tr = document.createElement('tr');
    tbody.appendChild(tr);
    for (var k in data2[i] ){
        var td = document.createElement("td");
        td.style.width = "15%";
        td.style.textAlign = "center";
        td.innerText = data2[i][k];
        tr.appendChild(td);
    }
}