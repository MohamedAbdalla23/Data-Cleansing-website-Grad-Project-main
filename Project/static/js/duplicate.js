var chart = document.querySelector("#chartt")
  var pers = document.getElementById("pers").value


  var options = {

    series: [pers],
    chart: {
      height: 290,
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
          background: '',
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
            formatter: function (val) {
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
    labels: ['%'],
  };

  var chart = new ApexCharts(document.querySelector("#chartt"), options);
  chart.render();


  
    // Function to save selected options to local storage
    function saveSelectedOptions() {
      var selectedTable = document.querySelector('#Table-name').value;
      var selectedColumns = [];
      var selectedOptions = document.querySelectorAll('#column-name option:checked');
      selectedOptions.forEach(option => selectedColumns.push(option.value));
  
      localStorage.setItem('selectedTable', selectedTable);
      localStorage.setItem('selectedColumns', JSON.stringify(selectedColumns));
    }
  
    // Function to retrieve and set selected options from local storage
    function setSelectedOptionsFromLocalStorage() {
      var selectedTable = localStorage.getItem('selectedTable');
      var selectedColumns = JSON.parse(localStorage.getItem('selectedColumns'));
  
      if (selectedTable) {
        document.querySelector('#Table-name').value = selectedTable;
      }
      if (selectedColumns) {
        selectedColumns.forEach(column => {
          var option = document.querySelector(`#column-name option[value="${column}"]`);
          if (option) {
            option.selected = true;
          }
        });
      }
    }
  
    // Call the function to set selected options from local storage when the page loads
    setSelectedOptionsFromLocalStorage();
  
    // Function to toggle visibility of columns select based on table selection
    function select() {
      var cols = document.getElementById("column-name");
      var tables = document.getElementById("Table-name");
      if (tables.value === 'Select Table') {
        cols.style.display = 'none';
      } else {
        cols.style.display = 'block';
      }
    }
  
    // Add an event listener to the table select to toggle visibility of columns select
    document.getElementById("Table-name").addEventListener('change', select);
  
    // Add an event listener to the form to save selected options before submitting
    document.querySelector('form').addEventListener('submit', saveSelectedOptions);