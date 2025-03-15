package types

import (
	"fmt"
	"time"
)

// LabelType represents the type of label
type LabelType string

const (
	// Label types
	LabelTypeBasicQA         LabelType = "basic_qa"
	LabelTypeTroubleshooting LabelType = "troubleshooting"
	LabelTypeResource        LabelType = "resource"
	LabelTypeDeployment      LabelType = "deployment"
	LabelTypeNetwork         LabelType = "network"
	LabelTypeServiceMesh     LabelType = "service_mesh"
	LabelTypeMultiCluster    LabelType = "multi_cluster"
)

// LabelFactory creates new labels of different types
type LabelFactory struct{}

// NewLabelFactory creates a new label factory
func NewLabelFactory() *LabelFactory {
	return &LabelFactory{}
}

// CreateLabel creates a new label of the specified type
func (f *LabelFactory) CreateLabel(labelType LabelType, question string) (Label, error) {
	now := time.Now()
	baseLabel := BaseLabel{
		ID:        fmt.Sprintf("%s-%d", labelType, now.Unix()),
		Question:  question,
		Timestamp: now,
	}

	switch labelType {
	case LabelTypeBasicQA:
		return &BasicQALabel{BaseLabel: baseLabel}, nil
	case LabelTypeTroubleshooting:
		return &TroubleshootingLabel{BaseLabel: baseLabel}, nil
	case LabelTypeResource:
		return &ResourceLabel{BaseLabel: baseLabel}, nil
	case LabelTypeDeployment:
		return &DeploymentLabel{BaseLabel: baseLabel}, nil
	case LabelTypeNetwork:
		return &NetworkLabel{BaseLabel: baseLabel}, nil
	case LabelTypeServiceMesh:
		return &ServiceMeshLabel{BaseLabel: baseLabel}, nil
	case LabelTypeMultiCluster:
		return &MultiClusterLabel{BaseLabel: baseLabel}, nil
	default:
		return nil, fmt.Errorf("unknown label type: %s", labelType)
	}
}

// ValidateLabel validates a label
func (f *LabelFactory) ValidateLabel(label Label) error {
	return label.Validate()
}
