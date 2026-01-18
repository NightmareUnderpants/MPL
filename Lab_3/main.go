package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"github.com/xuri/excelize/v2"
)

type VesselInfo struct {
	Name string
	IMO  string
	MMSI string
	Type string
}

var xlsxFile *excelize.File
var sheetName = "Vessels"
var fileName = "parsed_vessels.xlsx"
var readFileName = "Links.xlsx"

func main() {
	initXLSX()

	links := getLinksFromXLSX(readFileName)

	for _, urlAdress := range links {
		urlAdress = strings.Replace(urlAdress, " ", "%20", -1)

		fullURL := handleParseLink(urlAdress)
		if fullURL == "" {
			fmt.Println("Пропускаем - судно не найдено")
			continue
		}

		vessel := parse(fullURL)
		if vessel.Name == "" {
			fmt.Println("Пропускаем - не удалось получить данные судна")
			continue
		}

		addToXLSX(vessel)
	}
}

func getLinksFromXLSX(filename string) []string {
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		return nil
	}

	f, err := excelize.OpenFile(filename)
	if err != nil {
		return nil
	}
	defer f.Close()

	sheetName := f.GetSheetName(0)
	rows, err := f.GetRows(sheetName)
	if err != nil {
		return nil
	}

	links := make([]string, 0)

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) > 0 {
			links = append(links, row[0])
		}
	}

	return links
}

func getBody(url string) []byte {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatal(err)
	}

	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatal("Ошибка чтения тела ответа:", err)
	}

	return body
}

func handleParseLink(urlAdress string) string {
	body := getBody(urlAdress)

	doc, err := goquery.NewDocumentFromReader(strings.NewReader(string(body)))
	if err != nil {
		log.Fatal("Ошибка парсинга HTML:", err)
	}

	countText := doc.Find("div:contains('судно')").Text()

	if strings.Contains(countText, "1 судно") || strings.Contains(countText, "1 судов") {
		fmt.Println("Найдено ровно одно судно")

		link, exists := doc.Find("td a").Attr("href")
		if exists {
			fmt.Printf("Найдена ссылка: %s\n", link)

			fullURL := "https://www.vesselfinder.com" + link
			fmt.Printf("Полный URL: %s\n", fullURL)

			return fullURL
		} else {
			fmt.Println("Не удалось найти ссылку на судно")
		}
	} else {
		fmt.Println("Найдено не одно судно или судна отсутствуют")
	}
	return ""
}

func parse(url string) VesselInfo {
	vessel := VesselInfo{}

	if url == "" {
		return vessel
	}

	body := getBody(url)

	doc, err := goquery.NewDocumentFromReader(strings.NewReader(string(body)))
	if err != nil {
		fmt.Println("Ошибка парсинга HTML:", err)
		return vessel
	}

	// НАЗВАНИЕ
	text := doc.Find(".title").Text()

	vessel.Name = strings.TrimSpace(text)

	// MMSI и ТИП
	mmsi := ""
	shipType := ""
	imo := ""

	doc.Find("table.aparams tr").Each(func(i int, tr *goquery.Selection) {
		header := tr.Find("td.n3").Text()
		value := tr.Find("td.v3").Text()

		if strings.Contains(header, "MMSI") {
			if strings.Contains(header, "IMO") {
				parts := strings.Split(value, "/")
				if len(parts) >= 2 {
					imo = strings.TrimSpace(parts[0])
					mmsi = strings.TrimSpace(parts[1])
				}
			} else {
				mmsi = value
			}
		}
		if strings.Contains(header, "AIS тип") {
			shipType = value
		}
	})

	vessel.MMSI = mmsi
	vessel.Type = shipType
	vessel.IMO = imo

	fmt.Printf("Название судна: %s\n", text)
	fmt.Printf("MMSI: %s\n", vessel.MMSI)
	fmt.Printf("IMO: %s\n", vessel.IMO)
	fmt.Printf("Тип судна: %s\n", vessel.Type)

	return vessel
}

func initXLSX() {
	if _, err := os.Stat(fileName); err == nil {
		fmt.Printf("⚠️ Файл %s уже существует, пересоздаем...\n", fileName)
		os.Remove(fileName)
	}

	xlsxFile = excelize.NewFile()
	xlsxFile.DeleteSheet("Sheet1")

	if _, err := xlsxFile.NewSheet(sheetName); err != nil {
		log.Fatalf("Ошибка создания листа: %v", err)
	}

	headers := []string{
		"Название", "IMO", "MMSI", "Тип судна",
	}

	for col, header := range headers {
		cell, _ := excelize.CoordinatesToCellName(col+1, 1)
		if err := xlsxFile.SetCellValue(sheetName, cell, header); err != nil {
			log.Fatalf("Ошибка записи заголовка '%s': %v", header, err)
		}
	}

	if err := xlsxFile.SaveAs(fileName); err != nil {
		log.Fatalf("Ошибка сохранения XLSX файла: %v", err)
	}

	fmt.Printf("XLSX файл инициализирован: %s\n", fileName)
}

func addToXLSX(vessel VesselInfo) {
	if vessel.Name == "" {
		return
	}

	if xlsxFile == nil {
		var err error
		xlsxFile, err = excelize.OpenFile(fileName)
		if err != nil {
			log.Fatalf("Ошибка открытия файла %s: %v", fileName, err)
		}
	}

	rows, err := xlsxFile.GetRows(sheetName)
	if err != nil {
		log.Fatalf("Ошибка получения строк: %v", err)
	}

	nextRow := len(rows) + 1
	if nextRow == 1 {
		nextRow = 2
	}

	data := []interface{}{
		vessel.Name,
		vessel.IMO,
		vessel.MMSI,
		vessel.Type,
	}

	for col, value := range data {
		cell, err := excelize.CoordinatesToCellName(col+1, nextRow)
		if err != nil {
			log.Fatalf("Ошибка генерации координат ячейки: %v", err)
		}

		if err := xlsxFile.SetCellValue(sheetName, cell, value); err != nil {
			log.Fatalf("Ошибка записи значения '%v' в ячейку %s: %v", value, cell, err)
		}
	}

	if err := xlsxFile.Save(); err != nil {
		log.Fatalf("Ошибка сохранения изменений в XLSX: %v", err)
	}

	fmt.Printf("Добавлено судно: %s\n", vessel.Name)
}
