import React, { useEffect, useRef, useState } from "react";
import {
    Box,
    Checkbox,
    IconButton,
    InputAdornment,
    ListItemText,
    MenuItem,
    Select,
    Stack,
    TextField,
    Typography
} from "@mui/material";
import { CONDITION_KEYS, SELECT_OPTIONS, TIME_UNITS, TIME_VALUES } from "./Constants";
import ChipInput from "../../Shared/Chips/ChipInput";
import AddIcon from '@mui/icons-material/Add';
import { createTheme, ThemeProvider } from "@mui/material/styles";

type DynamicFieldRendererProps = {
  editMode: boolean;
  attributeKey: string;
  attributeValue: string;
  setAttributeValue: (value: string) => void;
  chips: string[];
  setChips: (value: string[]) => void;
  milestones: string[];
  setMilestones: (value: string[]) => void;
  otherValue: string;
  setOtherValue: (value: string) => void;
  options?: { label: string; value: string }[];
};

const DynamicFieldRenderer: React.FC<DynamicFieldRendererProps> = ({
  editMode,
  attributeKey,
  attributeValue,
  setAttributeValue,
  chips,
  setChips,
  milestones,
  setMilestones,
  otherValue,
  setOtherValue,
  options,
}) => {

    const [timeUnit, setTimeUnit] = useState<string>("");
    const [timeValue, setTimeValue] = useState<string>("");
    const [customTimeValue, setCustomTimeValue] = useState<string>("");
    const [error, setError] = useState(false);
    const [showCustomInput, setShowCustomInput] = useState(false);
    const [customMilestone, setCustomMilestone] = useState("");
    const [dynamicWidth, setDynamicWidth] = useState<number>(100);
    const textRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (textRef.current) {
            const totalLength = milestones.join(", ");
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");
            if (context) {
                const textWidth = context.measureText(totalLength).width;
                setDynamicWidth(Math.max(textWidth + 180, 200));
            }
        }
    }, [milestones]);

    const theme = createTheme({
        typography: {
            fontFamily: 'BC Sans',
        },
        components: {
          MuiSelect: {
            styleOverrides: {
              root: {
                "&.Mui-disabled": {
                  backgroundColor: "#EDEBE9",
                },
              },
            },
          },
          MuiOutlinedInput: {
            styleOverrides: {
              input: {
                "&.Mui-disabled": {
                  color: "#9F9D9C !important",
                },
              },
            },
          },
        },
    });

    useEffect(() => {
        if (timeUnit) {
            const value = customTimeValue || timeValue;
            if (value) {
                setAttributeValue(`${value} ${timeUnit}`);
            }
        }
    }, [timeValue, timeUnit, customTimeValue, setAttributeValue]);

    if (attributeKey === CONDITION_KEYS.TIME_ASSOCIATED_WITH_SUBMISSION_MILESTONE) {
        return (
            <Box
                sx={{
                    display: "flex",
                    flexDirection: "column",
                }}
            >
                <Select
                    value={timeUnit}
                    onChange={(e) => setTimeUnit(e.target.value)}
                    displayEmpty
                    fullWidth
                    sx={{
                        fontSize: "inherit",
                        lineHeight: "inherit",
                        width: editMode ? "30%" : "100%",
                        "& .MuiSelect-select": {
                            padding: "8px",
                        },
                        marginBottom: "10px",
                    }}
                >
                    <MenuItem value="" disabled sx={{ fontFamily: 'BC Sans' }}>
                        Select Time Unit
                    </MenuItem>
                    {TIME_UNITS.map((option) => (
                        <MenuItem key={option.value} value={option.label}>
                            {option.label}
                        </MenuItem>
                    ))}
                </Select>
                <ThemeProvider theme={theme}>
                    <Select
                        value={timeValue}
                        onChange={(e) => setTimeValue(e.target.value)}
                        displayEmpty
                        fullWidth
                        disabled={!timeUnit}
                        sx={{
                            fontSize: "inherit",
                            lineHeight: "inherit",
                            width: editMode ? "30%" : "100%",
                            "& .MuiSelect-select": {
                                padding: "8px",
                            },
                            marginBottom: "10px",
                        }}
                    >
                        <MenuItem value="" disabled sx={{ fontFamily: 'BC Sans' }}>
                            Select Time Value
                        </MenuItem>
                        {timeUnit && TIME_VALUES[timeUnit as keyof typeof TIME_VALUES].map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                                {option.label}
                            </MenuItem>
                        ))}
                    </Select>
                </ThemeProvider>
      
                {timeValue === "Other" ? (
                    <TextField
                        value={customTimeValue}
                        onChange={(e) => setCustomTimeValue(e.target.value)}
                        placeholder="Please specify"
                        size="small"
                        fullWidth
                        sx={{
                            flex: "0 0 auto",
                            width: editMode ? "30%" : "100%",
                        }}
                    />
                ) : null}
            </Box>
        );
    }

    if (attributeKey === CONDITION_KEYS.PARTIES_REQUIRED) {
        return (
            <ChipInput
                chips={chips}
                setChips={setChips}
                placeholder="Add a party"
                inputWidth={editMode ? "30%" : "100%"}
            />
        );
    }

    if (attributeKey === CONDITION_KEYS.MILESTONES_RELATED_TO_PLAN_IMPLEMENTATION) {
        const milestoneOptions = SELECT_OPTIONS[CONDITION_KEYS.MILESTONES_RELATED_TO_PLAN_IMPLEMENTATION];
    
        const handleAddCustomMilestone = () => {
            if (customMilestone.trim()) {
              setMilestones([...milestones, customMilestone]);
              setCustomMilestone(""); // Clear the input field
              setShowCustomInput(false); // Hide the custom input field
            }
        };

        return (
          <>
            <Select
                multiple // Enables multiple selection
                value={Array.isArray(milestones) ? milestones : []}
                onChange={(e) => setMilestones(e.target.value as string[])} // Handle multiple values
                renderValue={(selected) => (
                    <Box ref={textRef}>
                        {(selected as string[]).join(", ")}
                    </Box>
                )}
                fullWidth
                sx={{
                    fontSize: "inherit",
                    lineHeight: "inherit",
                    width: editMode ? `${dynamicWidth}px` : "100%",
                    minWidth: "30%",
                    "& .MuiSelect-select": {
                        padding: "8px",
                    },
                    marginBottom: "10px",
                }}
            >
                {milestoneOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                        <Checkbox checked={Array.isArray(milestones) && milestones.includes(option.value)} />
                        <ListItemText primary={option.label} />
                    </MenuItem>
                ))}
            </Select>

            <Typography
                variant="body2"
                color="primary"
                onClick={() => setShowCustomInput(true)}
                sx={{
                marginTop: "8px",
                cursor: "pointer",
                textDecoration: "underline",
                }}
            >
                + Other Milestone
            </Typography>

            {showCustomInput && (
                <div style={{ marginTop: "8px", display: "flex", alignItems: "center", gap: "8px" }}>
                    <TextField
                        value={customMilestone}
                        onChange={(e) => setCustomMilestone(e.target.value)}
                        placeholder="Enter custom milestone"
                        size="small"
                        fullWidth
                        sx={{
                            flex: "0 0 auto",
                            width: editMode ? "30%" : "100%",
                        }}
                        InputProps={{
                            endAdornment: customMilestone ? (
                              <InputAdornment position="end" sx={{ marginRight: "-5px" }}>
                                <IconButton
                                  onClick={handleAddCustomMilestone}
                                  sx={{
                                    padding: 0,
                                    borderRadius: "50%",
                                    backgroundColor: "green",
                                    color: "white",
                                    "&:hover": { backgroundColor: "darkgreen" },
                                  }}
                                >
                                  <AddIcon
                                    sx={{
                                        fontSize: "20px",
                                    }}
                                  />
                                </IconButton>
                              </InputAdornment>
                            ) : null,
                        }}
                    />
                </div>
            )}
          </>
        );
    }

    if (options) {
        return (
            <Stack direction="column">
                <Select
                    value={attributeValue}
                    onChange={(e) => setAttributeValue(e.target.value)}
                    fullWidth
                    sx={{
                        fontSize: "inherit",
                        lineHeight: "inherit",
                        width: editMode ? "30%" : "100%",
                        "& .MuiSelect-select": {
                        padding: "8px",
                        },
                    }}
                >
                    {options.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                        {option.label}
                    </MenuItem>
                    ))}
                </Select>
                {attributeValue === "Other" && (
                    <TextField
                        value={otherValue}
                        onChange={(e) => {
                            const value = e.target.value;
                            setOtherValue(value);
                            setError(value.trim() === "");
                        }}
                        size="small"
                        onBlur={() => {
                            if (!otherValue.trim()) {
                                setError(true);
                            }
                        }}
                        placeholder="Please specify"
                        fullWidth
                        error={error}
                        sx={{
                            width: editMode ? "30%" : "100%",
                            marginTop: "8px",
                            "& .MuiInputBase-root": {
                                padding: "0 0px",
                                fontSize: "inherit",
                                lineHeight: "inherit",
                            },
                            "& .MuiOutlinedInput-notchedOutline": {
                                border: error ? "1px solid red" : "none",
                            },
                            height: "1.5em",
                        }}
                    />
                )}
            </Stack>
        );
    }

    return (
        <TextField
            value={attributeValue}
            onChange={(e) => setAttributeValue(e.target.value)}
            fullWidth
            size="small"
            placeholder="Please specify"
            sx={{
                flex: "0 0 auto",
                width: editMode ? "30%" : "100%",
                "& .MuiInputBase-root": {
                  fontSize: "inherit",
                  lineHeight: "inherit",
                },
                "& .MuiOutlinedInput-notchedOutline": {
                  border: "none",
                },
                height: "1.5em",
            }}
        />
    );
};

export default DynamicFieldRenderer;
