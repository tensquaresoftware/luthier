#include "PluginEditor.h"

PluginEditor::PluginEditor(PluginProcessor& p)
    : AudioProcessorEditor(p), pluginProcessor_(p)
{
    setSize(400, 300);
}

void PluginEditor::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colours::black);
    g.setColour(juce::Colours::white);
    g.setFont(20.0f);
    g.drawFittedText("@PROJECT_DISPLAY_NAME@", getLocalBounds(), juce::Justification::centred, 1);
}

void PluginEditor::resized()
{
    // Position and size child components here.
}
