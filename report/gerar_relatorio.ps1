param([string]$OutPath)
$ErrorActionPreference = 'Stop'

# Built-in style ids (language independent)
$sNormal = -1; $sH1 = -2; $sH2 = -3; $sH3 = -4

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Add()
    $doc.PageSetup.PaperSize = 7          # A4
    foreach ($m in 'TopMargin','BottomMargin','LeftMargin','RightMargin') { $doc.PageSetup.$m = 70.9 }  # 2.5 cm

    $normal = $doc.Styles.Item($sNormal)
    $normal.Font.Name = 'Trebuchet MS'
    $normal.Font.Size = 11
    $normal.ParagraphFormat.SpaceAfter = 6
    $normal.ParagraphFormat.LineSpacingRule = 5   # multiple
    $normal.ParagraphFormat.LineSpacing = 13.8    # 1.15

    $sizes = @{ "-2" = 16; "-3" = 13; "-4" = 11.5 }
    foreach ($id in $sH1, $sH2, $sH3) {
        $st = $doc.Styles.Item($id)
        $st.Font.Name = 'Trebuchet MS'
        $st.Font.Size = [single]$sizes["$id"]
        $st.Font.Bold = $true
        $st.Font.Color = 0
        $st.ParagraphFormat.SpaceBefore = 12
        $st.ParagraphFormat.SpaceAfter = 6
    }
    $doc.Styles.Item($sH1).ParagraphFormat.PageBreakBefore = $true

    # Multilevel numbering 1 / 1.1 / 1.1.1 linked to the heading styles
    $lt = $doc.ListTemplates.Add($true)
    $formats = '%1', '%1.%2', '%1.%2.%3'
    $ids = $sH1, $sH2, $sH3
    for ($i = 1; $i -le 3; $i++) {
        $lvl = $lt.ListLevels.Item($i)
        $lvl.NumberFormat = $formats[$i - 1]
        $lvl.NumberStyle = 0
        $lvl.NumberPosition = 0
        $lvl.TextPosition = 0
        $lvl.TrailingCharacter = 2   # space
        $lvl.ResetOnHigher = $i - 1
        $lvl.LinkedStyle = $doc.Styles.Item($ids[$i - 1]).NameLocal
    }

    $sel = $word.Selection

    function Para([string]$text, [int]$style = -1, [int]$align = 0, [double]$size = 0, [bool]$bold = $false) {
        $sel.Style = $doc.Styles.Item($style).NameLocal
        $sel.ParagraphFormat.Alignment = $align
        if ($size -gt 0) { $sel.Font.Size = $size }
        $sel.Font.Bold = [int]$bold
        $sel.TypeText($text)
        $sel.TypeParagraph()
        $sel.Style = $doc.Styles.Item($sNormal).NameLocal
    }
    function Unnumbered([string]$text) {
        $sel.Style = $doc.Styles.Item($sH1).NameLocal
        $sel.TypeText($text)
        $sel.Range.ListFormat.RemoveNumbers()
        $sel.TypeParagraph()
    }

    # ---------------- Cover ----------------
    1..5 | ForEach-Object { Para '' }
    Para 'Volatility Interruptions and Crash Contagion in Euronext Lisbon' $sNormal 1 20 $true
    Para '' ; Para ''
    Para 'Authors:' $sNormal 1 12 $true
    Para 'João Paulo Ferreira Ribeiro (up202303467)' $sNormal 1 12
    Para 'Margarida Carvalhal Martins (up202303913)' $sNormal 1 12
    Para 'Matilde Barroso Costa (up202303970)' $sNormal 1 12
    Para 'Miguel Alexandre da Fonseca Leal (up202205197)' $sNormal 1 12
    Para 'Group 2' $sNormal 1 12
    Para ''
    Para 'Decision Support Systems' $sNormal 1 12 $true
    Para 'Luís Filipe Ribeiro dos Santos Guimarães' $sNormal 1 12
    Para 'Luís Gonçalo Rodrigues Reis Figueira' $sNormal 1 12
    Para 'Diogo Emanuel Pereira Miranda' $sNormal 1 12
    Para 'Nuno André Azevedo Marques' $sNormal 1 12
    1..4 | ForEach-Object { Para '' }
    Para "Master's Degree in Industrial Engineering and Management" $sNormal 1 12 $true
    Para ''
    Para '2026-12-02' $sNormal 1 12

    # ---------------- Front matter ----------------
    $sel.InsertBreak(7)   # page break
    Para 'Abstract' $sNormal 0 16 $true
    $sel.InsertBreak(7)
    Para 'Contents' $sNormal 0 16 $true
    $tocRange = $sel.Range
    $doc.TablesOfContents.Add($tocRange, $true, 1, 3) | Out-Null
    $sel.EndKey(6) | Out-Null
    $sel.TypeParagraph()
    $sel.InsertBreak(7)
    Para 'List of Figures' $sNormal 0 16 $true
    $sel.InsertBreak(7)
    Para 'List of Tables' $sNormal 0 16 $true

    # ---------------- Chapters ----------------
    $outline = @(
        @(1, 'Introduction'),
        @(2, 'Context and Motivation'),
        @(2, "Simulation's Objectives"),
        @(2, 'Report Structure'),
        @(1, 'Problem Description'),
        @(2, 'Euronext Lisbon and the PSI'),
        @(2, 'How a Market Fall Propagates'),
        @(2, 'Volatility Interruptions at Euronext'),
        @(2, 'Problem Statement and Research Questions'),
        @(1, 'Data and Stylised Facts'),
        @(2, 'Data Sources'),
        @(2, 'Stylised Facts of the BCP Stock'),
        @(2, 'Key Assumptions'),
        @(1, 'System Modelling'),
        @(2, 'Modelling Approach'),
        @(2, 'Implementation'),
        @(3, 'Main agent'),
        @(3, 'Order Book (Stock agent type)'),
        @(3, 'Volatility Interruptions and Reopening Auction'),
        @(3, 'Fundamentalist agent type'),
        @(3, 'Trend Follower agent type and Herding'),
        @(3, 'Noise Trader agent type'),
        @(3, 'Market Maker agent type'),
        @(3, 'News agent type'),
        @(1, 'Simulation Interface and User Controls'),
        @(2, 'Initial Setup Page'),
        @(2, 'Dashboard'),
        @(2, 'Data Export'),
        @(1, 'Verification, Calibration and Validation'),
        @(2, 'Order Book Tests'),
        @(2, 'Extreme Condition Tests'),
        @(2, 'Calibration'),
        @(2, 'Validation'),
        @(1, 'Experiments and Simulation Scenarios'),
        @(2, 'Baseline Scenario'),
        @(2, 'Large Shock with and without Collars'),
        @(2, 'Shock with a High Share of Trend Followers'),
        @(2, 'Collar Thresholds and Reservation Duration'),
        @(2, 'Optimal Thresholds'),
        @(2, 'Sensitivity Analysis'),
        @(2, 'Monte Carlo Replications'),
        @(1, 'Results'),
        @(2, 'Baseline Scenario'),
        @(2, 'Large Shock with and without Collars'),
        @(2, 'Shock with a High Share of Trend Followers'),
        @(2, 'Collar Thresholds and Reservation Duration'),
        @(2, 'Optimal Thresholds'),
        @(2, 'Sensitivity Analysis'),
        @(2, 'Monte Carlo Replications'),
        @(1, 'Discussion and Interpretation of Results'),
        @(1, 'Conclusions'),
        @(2, 'Final Considerations'),
        @(2, 'Limitations and Future Work')
    )
    $styleOf = @{ 1 = $sH1; 2 = $sH2; 3 = $sH3 }
    foreach ($h in $outline) {
        $sel.Style = $doc.Styles.Item($styleOf[$h[0]]).NameLocal
        $sel.TypeText($h[1])
        $sel.TypeParagraph()
    }

    Unnumbered 'References'
    foreach ($a in 'APPENDIX A: Model Parameters and Initial Configuration',
                   'APPENDIX B: Simulation Dashboard',
                   'APPENDIX C: Order Book Test Output',
                   'APPENDIX D: Calibration Log',
                   'APPENDIX E: Assumptions Register',
                   'APPENDIX F: Results Excel File',
                   'APPENDIX G: Experiment Interfaces (Parameter Variation and Monte Carlo)') { Unnumbered $a }

    # ---------------- Page numbers in the footer ----------------
    $footer = $doc.Sections.Item(1).Footers.Item(1)
    $footer.PageNumbers.Add(1, $true) | Out-Null   # centre
    $doc.Sections.Item(1).PageSetup.DifferentFirstPageHeaderFooter = $true

    $doc.TablesOfContents.Item(1).Update()
    $doc.SaveAs2($OutPath, 16)                       # .docx
    $pdf = [System.IO.Path]::ChangeExtension($OutPath, '.pdf')
    $doc.SaveAs2($pdf, 17)                           # PDF copy for checking
    $doc.Close($false)
    "OK $OutPath"
}
catch { Write-Output ("ERRO: " + $_.Exception.Message + " | " + $_.InvocationInfo.PositionMessage) }
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
