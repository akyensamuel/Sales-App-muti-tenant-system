
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const chartLabels = [
            
                'August 2024',
            
                'September 2024',
            
                'October 2024',
            
                'November 2024',
            
                'December 2024',
            
                'January 2025',
            
                'February 2025',
            
                'March 2025',
            
                'April 2025',
            
                'May 2025',
            
                'June 2025',
            
                'July 2025'
            
        ];
        
        const chartData = [
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                0.0,
            
                20371.0
            
        ];
        
        console.log('Chart labels:', chartLabels);
        console.log('Chart data:', chartData);
        
        const revenueChart = new Chart(document.getElementById('revenueChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [{
                    label: 'Monthly Revenue',
                    data: chartData,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    });
</script>
