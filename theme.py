"""theme.py — global dark theme (Catppuccin Mocha palette)."""
import dearpygui.dearpygui as dpg

# ── Palette ───────────────────────────────────────────────────────────────────
BG_BASE    = (30,  30,  46,  255)   # main window / canvas bg
BG_MANTLE  = (24,  24,  37,  255)   # deeper panels, child bg
BG_CRUST   = (17,  17,  27,  255)   # darkest: scrollbar bg, title, menubar
SURFACE_0  = (49,  50,  68,  255)   # input / frame bg
SURFACE_1  = (69,  71,  90,  255)   # hover, separators, scrollbar grab
SURFACE_2  = (88,  91,  112, 255)   # active, strong borders

ACCENT     = (137, 180, 250, 255)   # blue highlight: checkmark, slider
ACCENT_DIM = (100, 140, 210, 200)   # button base
ACCENT_HOV = (120, 162, 240, 220)   # button hover
ACCENT_ACT = (150, 190, 255, 255)   # button active / grabbed

TEXT       = (205, 214, 244, 255)   # main text
TEXT_DIM   = (127, 132, 156, 255)   # disabled / placeholder

HEADER     = (49,  50,  68,  170)   # collapsing header resting
HEADER_HOV = (69,  71,  90,  190)
HEADER_ACT = (88,  91,  112, 210)

SEP        = (69,  71,  90,  200)   # separator line


def apply_theme() -> None:
    with dpg.theme() as _theme:
        with dpg.theme_component(dpg.mvAll):
            # ── Backgrounds ──────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg,        BG_BASE)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg,         BG_MANTLE)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg,         BG_MANTLE)
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg,       BG_CRUST)

            # ── Borders ───────────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_Border,          SURFACE_1)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow,    (0, 0, 0, 0))

            # ── Input / frame ─────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg,         SURFACE_0)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,  SURFACE_1)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,   SURFACE_2)

            # ── Title bar ─────────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg,          BG_CRUST)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,    BG_MANTLE)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, BG_CRUST)

            # ── Buttons ───────────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_Button,          ACCENT_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,   ACCENT_HOV)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,    ACCENT_ACT)

            # ── Collapsing headers ────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_Header,          HEADER)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered,   HEADER_HOV)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive,    HEADER_ACT)

            # ── Text ──────────────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_Text,            TEXT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled,    TEXT_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg,  (137, 180, 250, 90))

            # ── Scrollbar ─────────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg,           BG_CRUST)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab,         SURFACE_1)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered,  SURFACE_2)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive,   ACCENT_DIM)

            # ── Separators ────────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_Separator,        SEP)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, SURFACE_2)
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive,  ACCENT)

            # ── Interactive ───────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark,        ACCENT)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab,       ACCENT_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, ACCENT_ACT)
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip,        (137, 180, 250,  50))
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGripHovered, (137, 180, 250, 140))
            dpg.add_theme_color(dpg.mvThemeCol_ResizeGripActive,  ACCENT)

            # ── Tables ────────────────────────────────────────────────────────
            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg,     BG_MANTLE)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong,  SURFACE_1)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight,   SURFACE_0)
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBg,         (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt,      (24, 24, 37, 60))

            # ── Styles ────────────────────────────────────────────────────────
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding,    6.0)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding,     4.0)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,     4.0)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding,     6.0)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 4.0)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding,      4.0)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding,       4.0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize,  1.0)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize,   0.0)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize,     12.0)
            dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize,       10.0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,     10, 10)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding,       6,  4)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,        8,  6)

    dpg.bind_theme(_theme)
