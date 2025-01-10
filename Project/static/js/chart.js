pers=document.getElementById('pers').value
console.log(pers)
var chart = document.querySelector("#chart66")
  var options = {

    series: [pers],
    chart: {
    height: 300,
    type: 'radialBar',
    toolbar: {
      show: true
    }
  },
  plotOptions: {
    radialBar: {
      startAngle: -135,
      endAngle: 225,
       hollow: {
        margin: 0,
        size: '70%',
        background: '',
        image: undefined,
        imageOffsetX: 0,
        imageOffsetY: 0,
        position: 'front',
        dropShadow: {
          enabled: true,
          top: 3,
          left: 0,
          blur: 4,
          opacity: 0.24
        }
      },
      track: {
        background: '#',
        strokeWidth: '67%',
        margin: 0, // margin is in pixels
        dropShadow: {
          enabled: true,
          top: -3,
          left: 0,
          blur: 4,
          opacity: 0.35
        }
      },
  
      dataLabels: {
        show: true,
        name: {
          offsetY: -10,
          show: true,
          color: 'white',
          fontSize: '17px'
        },
        value: {
          formatter: function(val) {
            return parseInt(val);
          },
          color: 'white',
          fontSize: '36px',
          show: true,
        }
      }
    }
  },
  fill: {
    type: 'gradient',
    gradient: {
      shade: 'dark',
      type: 'horizontal',
      shadeIntensity: 0.5,
      gradientToColors: ['#45D075'],
      inverseColors: true,
      opacityFrom: 1,
      opacityTo: 1,
      stops: [0, 100]
    }
  },
  stroke: {
    lineCap: 'round'
  },
  labels: ['Percent'],
  };

  var chart = new ApexCharts(document.querySelector("#chart66"), options);
  chart.render();

  function deleteRow(row) {
    row.remove();
}

function editRow(row) {
    var cells = row.cells;
    for (var j = 0; j < cells.length - 1; j++) {
        var cell = cells[j];
        var currentValue = cell.textContent;
        cell.innerHTML = '<input type="text" class="form-control" value="' + currentValue + '">';
    }
    row.querySelector('.update-icon').style.display = 'none';
    row.querySelector('.save-icon').style.display = '';
    row.querySelector('.cancel-icon').style.display = '';
}

function saveRow(row) {
    var cells = row.cells;
    for (var j = 0; j < cells.length - 1; j++) {
        var cell = cells[j];
        var newValue = cell.querySelector('input').value;
        cell.textContent = newValue;
    }
    row.querySelector('.update-icon').style.display = '';
    row.querySelector('.save-icon').style.display = 'none';
    row.querySelector('.cancel-icon').style.display = 'none';

    // Show success message
    var successMessage = document.getElementById("successMessage");
    successMessage.style.display = "block";
    setTimeout(function(){
        successMessage.style.display = "none";
    }, 3000); // Hide after 3 seconds (3000 milliseconds)
}

function cancelEditRow(row) {
    var cells = row.cells;
    for (var j = 0; j < cells.length - 1; j++) {
        var cell = cells[j];
        cell.innerHTML = cell.querySelector('input').defaultValue;
    }
    row.querySelector('.update-icon').style.display = '';
    row.querySelector('.save-icon').style.display = 'none';
    row.querySelector('.cancel-icon').style.display = 'none';
}   