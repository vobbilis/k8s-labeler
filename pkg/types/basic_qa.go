package types

// BasicQALabel represents the simplest label format for QA pairs
type BasicQALabel struct {
	BaseLabel
	Answer  string  `json:"answer"`
	Context Context `json:"context"`
}

// Validate implements the Label interface
func (b *BasicQALabel) Validate() error {
	// TODO: Implement validation logic
	return nil
}
