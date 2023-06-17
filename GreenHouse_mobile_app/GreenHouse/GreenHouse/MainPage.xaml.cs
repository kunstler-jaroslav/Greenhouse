using Microcharts;
using SkiaSharp;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using System.Net.Http;
using Newtonsoft.Json.Linq;
using System.IO;
using System.Globalization;

namespace GreenHouse
{
    public class GreenhouseData
    {
        public string CreationDateTime { get; set; }
        public float Temperature { get; set; }
        public float AirHumidity { get; set; }
        public float SoilHumidity { get; set; }
        public float WindowsOpened { get; set; }
    }


    public partial class MainPage : ContentPage
    {
        private int HISTORY_AMOUNT = 25;
        private bool chb_mot = false;
        private bool chb_air = false;
        private bool chb_soil = false;
        private bool chb_tem = false;
        private string water_id = "012";
        
        // api links
        private string BASE_PATH = "https://your-api-link.onrender.com/";
        private string OPEN_POST_PATH = "open-post";
        private string OPEN_ACTUAL_PATH = "open-actual";
        private string DATA_ACTUAL_PATH = "data-actual";
        private string DATA_ALL_PATH = "data-all";
        private static readonly HttpClient client = new HttpClient();

        public List<float> TemperatureHistory { get; set; } = null;
        public List<float> AirHumidityHistory { get; set; } = null;
        public List<float> SoilHumidityHistory { get; set; } = null;
        public List<float> WindowsOpenedHistory { get; set; } = null;

        
        public MainPage()
        {
            InitializeComponent();
            get_show_open();
            get_show_data_actual();
            get_data_all_start();
            water_id = DateTime.Now.ToString();
        }

        //--------------------------------------------------------------------------------------------------------------------------------------------
        // Visualization for graphs

        private void visualize_temp_history(List<float> distances, SKColor col)
        {
            var entries = new List<ChartEntry>();
            int i = 0;
            int m = distances.Count;
            foreach (float CurrentData in distances)
            {
                if (m - i < HISTORY_AMOUNT)
                {
                    entries.Add(new ChartEntry(CurrentData)
                    {
                        Label = CurrentData.ToString(),
                        Color = col
                    });
                }
                ++i;
            }
            chartViewTemp.Chart = new LineChart() { Entries = entries, ValueLabelOrientation = Orientation.Horizontal, LabelTextSize = 40, AnimationDuration = TimeSpan.FromSeconds(1), MaxValue = 100, LabelOrientation = Orientation.Horizontal, BackgroundColor = SKColors.Transparent, LabelColor = SKColors.Transparent, PointSize = 0, Margin = 0 };
        }

        private void visualize_air_history(List<float> distances, SKColor col)
        {
            var entries = new List<ChartEntry>();
            int i = 0;
            int m = distances.Count;
            foreach (float CurrentData in distances)
            {
                if (m - i < HISTORY_AMOUNT)
                {
                    entries.Add(new ChartEntry(CurrentData)
                    {
                        Label = CurrentData.ToString(),
                        Color = col
                    });
                }
                ++i;
            }
            chartViewAir.Chart = new LineChart() { LineAreaAlpha = 0, Entries = entries, ValueLabelOrientation = Orientation.Horizontal, LabelTextSize = 40, AnimationDuration = TimeSpan.FromSeconds(1), MaxValue = 150, LabelOrientation = Orientation.Horizontal, BackgroundColor = SKColors.Transparent, LabelColor = SKColors.Transparent, PointSize = 0, Margin = 0 };
        }

        private void visualize_soil_history(List<float> distances, SKColor col)
        {
            var entries = new List<ChartEntry>();
            int i = 0;
            int m = distances.Count;
            foreach (float CurrentData in distances)
            {
                if (m - i < HISTORY_AMOUNT)
                {
                    entries.Add(new ChartEntry(CurrentData)
                    {
                        Label = CurrentData.ToString(),
                        Color = col
                    });
                }
                ++i;
            }
            chartViewSoil.Chart = new LineChart() { LineAreaAlpha = 0, Entries = entries, ValueLabelOrientation = Orientation.Horizontal, LabelTextSize = 40, AnimationDuration = TimeSpan.FromSeconds(1), MaxValue = 150, LabelOrientation = Orientation.Horizontal, BackgroundColor = SKColors.Transparent, LabelColor = SKColors.Transparent, PointSize = 0, Margin = 0 };
        }

        private void visualize_window_history(List<float> distances, SKColor col)
        {
            var entries = new List<ChartEntry>();
            int i = 0;
            int m = distances.Count;
            foreach (float CurrentData in distances)
            {
                if (m - i < HISTORY_AMOUNT)
                {
                    entries.Add(new ChartEntry(CurrentData)
                    {
                        Label = CurrentData.ToString(),
                        Color = col
                    });
                }
                ++i;
            }
            chartViewWindow.Chart = new LineChart() { LineAreaAlpha = 0, Entries = entries, ValueLabelOrientation = Orientation.Horizontal, LabelTextSize = 40, AnimationDuration = TimeSpan.FromSeconds(1), MaxValue = 150, LabelOrientation = Orientation.Horizontal, BackgroundColor = SKColors.Transparent, LabelColor = SKColors.Transparent, PointSize = 0, Margin = 0 };
        }

        //--------------------------------------------------------------------------------------------------------------------------------------------
        // Greenhouse data loading and processing

        // Get and show actual data
        private async void get_show_data_actual()
        {
            string path = BASE_PATH + DATA_ACTUAL_PATH;
            GreenhouseData data = await GetDataActualAsync(path);
            if(data.AirHumidity == -1 || data.AirHumidity == -1 || data.SoilHumidity == -1)
            {
                await Application.Current.MainPage.DisplayAlert("Data refresh failed", "It was not possible to load data from greenhous. Check your internet connection.", "OK");
            }
            else
            {
                lbl_temp.Text = data.Temperature.ToString() + "°C";
                lbl_airhum.Text = data.AirHumidity.ToString() + "%";
                lbl_soilhum.Text = data.SoilHumidity.ToString() + "%";
                lbl_windopen.Text = data.WindowsOpened.ToString() + "%";
                string date = data.CreationDateTime.ToString();
                lbl_last_refresh.Text = "Data from: " + date;
            }
        }

        static async Task<GreenhouseData> GetDataActualAsync(string path)
        {
            GreenhouseData data = new GreenhouseData();
            data.Temperature = -1;
            data.AirHumidity = -1;
            data.SoilHumidity = -1;
            data.WindowsOpened = -1;
            try
            {
                HttpResponseMessage response = await client.GetAsync(path);
                String responseContent = await response.Content.ReadAsStringAsync();
                JObject json_data = JObject.Parse(responseContent);
                data.Temperature = (float)json_data["Temperature"];
                data.AirHumidity = (float)json_data["AirHumidity"];
                data.SoilHumidity = (float)json_data["SoilHumidity"];
                data.WindowsOpened = (float)json_data["WindowsOpened"];
                data.CreationDateTime = (string)json_data["CreationDateTime"];
                
            }
            catch { }
            return data;
        }

        // Get and visualize graph data
        private async void get_data_all()
        {
            List<float>[] history = await GetDataAllAsync(BASE_PATH + DATA_ALL_PATH);
            TemperatureHistory = history[0];
            AirHumidityHistory = history[1];
            SoilHumidityHistory = history[2];
            WindowsOpenedHistory = history[3];
        }

        private async void get_data_all_start()
        {
            TemperatureHistory = null;
            while (TemperatureHistory == null)
            {
                List<float>[] history = await GetDataAllAsync(BASE_PATH + DATA_ALL_PATH);
                TemperatureHistory = history[0];
                AirHumidityHistory = history[1];
                SoilHumidityHistory = history[2];
                WindowsOpenedHistory = history[3];
                chb_temp.IsChecked = true;
                await Task.Delay(2000);
            }
            
            visualize_temp_history(TemperatureHistory, SKColors.Red);
        }

        static async Task<List<float>[]> GetDataAllAsync(string path)
        {
            List<float> Temps = new List<float>();
            List<float> AirHums = new List<float>();
            List<float> SoilHums = new List<float>();
            List<float> WindOpens = new List<float>();
            try
            {
                HttpResponseMessage response = await client.GetAsync(path);
                String responseContent = await response.Content.ReadAsStringAsync();
                responseContent = responseContent.Substring(1, responseContent.Length - 2);

                string[] substrings = responseContent.Split(new string[] { "}, " }, StringSplitOptions.None);
                foreach (string substring in substrings)
                {
                    string subst = substring;
                    if (substring[substring.Length - 1] != '}')
                        subst += "}";

                    JObject json_data = JObject.Parse(subst);
                    Temps.Add((float)json_data["Temperature"]);
                    AirHums.Add((float)json_data["AirHumidity"]);
                    SoilHums.Add((float)json_data["SoilHumidity"]);
                    WindOpens.Add((float)json_data["WindowsOpened"]);
                }
            }
            catch { }
            List<float>[] re = new List<float>[4];
            re[0] = Temps;
            re[1] = AirHums;
            re[2] = SoilHums;
            re[3] = WindOpens;
            return re;
        }

        //--------------------------------------------------------------------------------------------------------------------------------------------
        // Checkbox handel
        private void chb_temp_oncheck(object sender, CheckedChangedEventArgs e)
        {
            if(TemperatureHistory != null)
            {
                chb_tem = !chb_tem;
                if (chb_tem)
                {
                    visualize_temp_history(TemperatureHistory, SKColors.Red);
                }
                else
                {
                    visualize_temp_history(TemperatureHistory, SKColors.Transparent);
                }
            }
        }

        private void chb_air_hum_oncheck(object sender, CheckedChangedEventArgs e)
        {
            if (AirHumidityHistory != null)
            {
                chb_air = !chb_air;
                if (chb_air)
                {
                    chartViewAir.IsVisible = true;
                    visualize_air_history(AirHumidityHistory, SKColors.Green);
                }
                else
                {
                    chartViewAir.IsVisible = false;
                    visualize_air_history(AirHumidityHistory, SKColors.Transparent);
                }
            }
        }

        private void chb_soil_hum_oncheck(object sender, CheckedChangedEventArgs e)
        {
            if (SoilHumidityHistory != null)
            {
                chb_soil = !chb_soil;
                if (chb_soil)
                {
                    chartViewSoil.IsVisible = true;
                    visualize_soil_history(SoilHumidityHistory, SKColors.Blue);
                }

                else
                {
                    chartViewSoil.IsVisible = false;
                    visualize_soil_history(SoilHumidityHistory, SKColors.Transparent);
                }
            }
        }

        private void chb_mot_open_oncheck(object sender, CheckedChangedEventArgs e)
        {
            if (WindowsOpenedHistory != null)
            {
                chb_mot = !chb_mot;
                if (chb_mot)
                {
                    chartViewWindow.IsVisible = true;
                    visualize_window_history(WindowsOpenedHistory, SKColors.Gray);
                }

                else
                {
                    chartViewWindow.IsVisible = false;
                    visualize_window_history(WindowsOpenedHistory, SKColors.Transparent);
                }
            }
        }

        //--------------------------------------------------------------------------------------------------------------------------------------------
        // Button handel

        private int last_on = 2;

        // button clicked
        private void btn_open_clicked(object sender, EventArgs e)
        {
            btn_open_clicked_show();
            send_open(1);
        }

        private void btn_auto_clicked(object sender, EventArgs e)
        {
            btn_auto_clicked_show();
            send_open(2);
        }

        private void btn_close_clicked(object sender, EventArgs e)
        {
            btn_close_clicked_show();
            send_open(3);
        }

        private void graph_refresh_clicked(object sender, EventArgs e)
        {
            get_data_all_start();
        }

        private void data_refresh_clicked(object sender, EventArgs e)
        {
            get_show_data_actual();
        }

        // user inteface actions
        private void set_last_show(int data)
        {
            switch (data)
            {
                case 1:
                    btn_open_clicked_show();
                    return;
                case 2:
                    btn_auto_clicked_show();
                    return;
                case 3:
                    btn_close_clicked_show();
                    return;
            }
        }

        private void btn_open_clicked_show()
        {
            lbl_open.FontSize = 20;
            lbl_open.VerticalOptions = LayoutOptions.End;
            lbl_auto.FontSize = 10;
            lbl_auto.VerticalOptions = LayoutOptions.Center;
            lbl_close.FontSize = 10;
            lbl_close.VerticalOptions = LayoutOptions.Center;
        }

        private void btn_auto_clicked_show()
        {
            lbl_auto.FontSize = 20;
            lbl_auto.VerticalOptions = LayoutOptions.End;
            lbl_open.FontSize = 10;
            lbl_open.VerticalOptions = LayoutOptions.Center;
            lbl_close.FontSize = 10;
            lbl_close.VerticalOptions = LayoutOptions.Center;
        }

        private void btn_close_clicked_show()
        {
            lbl_open.FontSize = 10;
            lbl_open.VerticalOptions = LayoutOptions.Center;
            lbl_auto.FontSize = 10;
            lbl_auto.VerticalOptions = LayoutOptions.Center;
            lbl_close.FontSize = 20;
            lbl_close.VerticalOptions = LayoutOptions.End;
        }
        
        // put api requests
        private async void send_open(int data)
        {
            bool response = await SendOpenDataAsync(BASE_PATH + OPEN_POST_PATH, data, water_id);
            if (!response)
            {
                await Application.Current.MainPage.DisplayAlert("Failed", "It was not possible to send instructions to greenhouse. Check your internet connection.", "OK");
                set_last_show(last_on);
            }
            else
            {
                last_on = data;
            }
        }

        static async Task<Boolean> SendOpenDataAsync(string path, int oac, string waterid)
        {
            string data = "{\"open\": \" " + oac.ToString() +"\"" + ", " + "\"waterid\": \"" + waterid.ToString() + "\"}";
            // Create a StringContent object with the JSON string
            StringContent content = new StringContent(data, Encoding.UTF8, "application/json");

            // Send a POST request with the JSON data to the API endpoint
            try
            {
                HttpResponseMessage response = await client.PutAsync(path, content);
            }
            catch 
            {
                return false;
            }
            return true;
        }

        // get api request
        private async void get_show_open()
        {
            string path = BASE_PATH + OPEN_ACTUAL_PATH;
            int oac = await GetOpenDataAsync(path);
            if(oac == -1)
                await Application.Current.MainPage.DisplayAlert("Refresh failed", "It was not possible to load data from greenhous. Check your internet connection.", "OK");
            last_on = oac;
            set_last_show(oac);
        }

        static async Task<int> GetOpenDataAsync(string path)
        {
            int data;
            try
            {
                HttpResponseMessage response = await client.GetAsync(path);
                String responseContent = await response.Content.ReadAsStringAsync();
                JObject json_data = JObject.Parse(responseContent);
                data = (int)json_data["open"];
            }
            catch 
            {
                return -1;
            }
            return data;
        }

        private void btn_water_clicked(object sender, EventArgs e)
        {
            water_id = DateTime.Now.ToString();
            send_open(last_on);
        }
    }
}
